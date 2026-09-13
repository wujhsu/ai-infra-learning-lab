import reading from './reading.json';
import stages from './stages.json';
export {reading,stages};
export const asset=(path:string)=>`${import.meta.env.BASE_URL}${path.replace(/^\//,'')}`;
export const lessonUrl=(id:string)=>asset(`read/${id}/`);
