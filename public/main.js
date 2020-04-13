import { newPath } from './form.js';
var pathId = 0
function addPathAction(){
    pathId = newPath(pathId, "paths")
}