/**
 * 
 * @author Roman Machala
 * @date 14.04.2025
 * @brief Script to handle audio dataset uploading logic
 * 
 */

import { startEvaluation } from "./handleEval.js";
import { showModal, updateModalText, hideModal } from "./handleAnalysis.js";

/**
 * 
 * Event listener for uploading files, starts when submit button is pressed
 * 
 */
document.getElementById("upload-form-audios").addEventListener("submit", function (event){
  event.preventDefault();
  uploadAudios();
});

/**
 * 
 * @brief simple function for dataset uploading
 * 
 */
async function uploadAudios(){
  const input = document.getElementById('folderInput');
  const formData = new FormData();
  const files = input.files;

  const rootFolderName = files[0].webkitRelativePath.split('/')[0];
  // uses relative paths

  for (const file of files) {
    formData.append(file.webkitRelativePath, file);
  }
  showModal("Uploading files.");
  try{
    // uploads files to the application
    fetch('/upload-files', {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (response.ok) {
        updateModalText("Starting evaluation");
        console.log("Files were uploaded.");
        startEvaluation(rootFolderName);
      } else {
        updateModalText("Files couldn't be uploaded.");
        console.error("Files couldn't be uploaded.");
      }
    });
  }catch (e){
    updateModalText("An error occured while trying to upload files");
    console.log("An error occured while trying to upload audios");
  }finally{
    hideModal();
  }
}
