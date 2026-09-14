import readingData from './reading.json';
import projectsData from './projects.json';
export type ReadingEntry={id:string;title:string;order:number};
export type ProjectPhase={title:string;outcome:string;chapters:string[]};
export type Project={id:string;label:string;title:string;outcome:string;labStatus:string;chapters:string[];phases:ProjectPhase[]};
export const reading=readingData as ReadingEntry[];
export const projects=projectsData as unknown as Project[];
export const asset=(path:string)=>`${import.meta.env.BASE_URL}${path.replace(/^\//,'')}`;
export const lessonUrl=(id:string)=>asset(`read/${id}/`);
