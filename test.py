# import pytorch library
import torch
# check for GPU
if not torch.cuda.is_available():
    print('GPU not available.')
# necessary imports
import fastai
from deoldify.visualize import *
import warnings
warnings.filterwarnings("ignore", 
                        category=UserWarning, message=".*?Your .*? set is empty.*?")

  
# use the get image colorizer function with artistic model
colorizer = get_image_colorizer(artistic=True) #@param {type:"string"}
  
# Here, we provide the parameters such as source URL, render factor etc.
source_url = "https://firebasestorage.googleapis.com/v0/b/repixelizor-380005.appspot.com/o/105067464298105617131%2Fupload%2F2023-03%2FIMG_1307.JPG?alt=media&token=62d25ae3-c055-4b57-ae24-0775af002160"

render_factor = 39  #@param {type: "slider", min: 7, max: 40}
watermarked = False #@param {type:"boolean"}
  
if source_url is not None and source_url !='':
    image_path = colorizer.plot_transformed_image_from_url(url=source_url, 
          render_factor=render_factor, compare=True, watermarked=watermarked)
    print(image_path)
    # show_image_in_notebook(image_path)
else:
    print('Provide the valid image URL.')