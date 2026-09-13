"""Meaningful mechanism and recovery checks. Requires the separate torch lab env."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'labs/tiny_model'))
try:
    import torch
except ImportError:
    torch = None
if torch:
    from model import TinyLM, save_checkpoint, load_checkpoint
    from train import train_step, INPUT, TARGET

@unittest.skipIf(torch is None,'torch lab environment not installed')
class TinyModelTest(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(7)
        torch.set_num_threads(1)
        self.model = TinyLM().eval()

    def test_cached_incremental_and_chunked_match_full_causal_logits(self):
        ids = torch.tensor([[0,1,2,3,4,5]])
        with torch.no_grad():
            full,_ = self.model(ids)
            cache=None; outputs=[]
            for i in range(ids.shape[1]):
                logits,cache=self.model(ids[:,i:i+1],cache);outputs.append(logits)
            torch.testing.assert_close(full,torch.cat(outputs,dim=1),atol=2e-6,rtol=2e-5)
            _,cache=self.model(ids[:,:3]);last,_=self.model(ids[:,3:],cache)
            torch.testing.assert_close(full[:,3:],last,atol=2e-6,rtol=2e-5)

    def test_future_tokens_cannot_change_prefix(self):
        with torch.no_grad():
            a,_=self.model(torch.tensor([[0,1,2,3]]))
            b,_=self.model(torch.tensor([[0,1,4,5]]))
        torch.testing.assert_close(a[:,:2],b[:,:2])
        self.assertGreater((a[:,2:]-b[:,2:]).abs().max().item(),1e-3)

    def test_gradient_matches_finite_difference(self):
        self.model.double()
        def loss():return torch.nn.functional.cross_entropy(self.model(INPUT)[0].reshape(-1,7),TARGET.reshape(-1))
        loss().backward();p=self.model.head.weight
        analytic=p.grad[0,0].item();eps=1e-5
        with torch.no_grad():
            original=p[0,0].item();p[0,0]=original+eps;plus=loss().item()
            p[0,0]=original-eps;minus=loss().item();p[0,0]=original
        self.assertAlmostEqual(analytic,(plus-minus)/(2*eps),places=6)

    def test_checkpoint_resume_preserves_next_updates(self):
        optimizer=torch.optim.AdamW(self.model.parameters(),lr=.01)
        for _ in range(8):train_step(self.model,optimizer)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'checkpoint.pt';save_checkpoint(path,self.model,optimizer,8)
            expected=[train_step(self.model,optimizer) for _ in range(3)]
            other,opt,step=load_checkpoint(path)
            actual=[train_step(other,opt) for _ in range(3)]
            self.assertEqual(step,8);self.assertEqual(expected,actual)
            for a,b in zip(self.model.parameters(),other.parameters()):torch.testing.assert_close(a,b,rtol=0,atol=0)

    def test_training_reduces_loss_and_generation_matches(self):
        optimizer=torch.optim.AdamW(self.model.parameters(),lr=.01)
        start=train_step(self.model,optimizer)
        for _ in range(79):last=train_step(self.model,optimizer)
        self.assertLess(last,start/20)
        prompt=torch.tensor([[0,1,2,3]])
        self.assertEqual(self.model.generate(prompt).tolist(),[[0,1,2,3,4,5,6]])
        self.assertTrue(torch.equal(self.model.generate(prompt),self.model.generate(prompt,use_cache=False)))

if __name__=='__main__':unittest.main()
