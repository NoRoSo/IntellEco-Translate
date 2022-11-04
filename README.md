# IntellEco-Translate
Made for the Carbon Hack 2022 competition, these are the files that were made. The team consists of Noe Soto, Ziliang Zong, and Lucia Ye.
# Contact info:
<ul>
  <li>Noe Soto (Backend & Frontend): fairfieldns@gmail.com</li>
  <li>Ziliang Zong (Backend & VM Setup): ziliang@txstate.edu</li>
  <li>Lucia Ye (Frontend Designs & Video): lu.ye@network.rca.ac.uk</li>
</ul>

# How to Use
### Getting Carbon Aware SDK Setup
Firstly, you must setup the <a href="https://github.com/Green-Software-Foundation/carbon-aware-sdk">Carbon Aware SDK</a> WebAPI. Use this link to set it up!

### Using Gradio.io & Translation.py
The code utilizes <a href="https://gradio.app/docs/">Gradio</a> in order to host the AI models on Azure Cloud. Click on the link to become familiar with the tools!  
Gradio was utilized in ```translation.py```. Once the program is executed, it will generate a link that you will use in ```api.py```.

### Preparing api.py
The python libraries used in api.py were:
<ul>
  <li><a href="https://flask.palletsprojects.com/en/2.2.x/">Flask</a></li>
  <li><a href="https://flask-cors.readthedocs.io/en/latest/">Flask-CORS</a></li>
  <li><a href="https://geocoder.readthedocs.io/">Geocoder</a></li>
  <li><a href="https://pypi.org/project/requests/">Requests</a></li>
</ul>

After installing the libraries for ```api.py```, you can run the program, but if you try to use the website, it will most likely error because the gradio links do not exist. In the previous step, ```translation.py``` will generate these links for you, so copy and paste those links into their respective region. Secondly, you will need to make sure that the Carbon Aware SDK WebAPI is running and if necessary, you will have to update the links at the top of ```api.py``` to redirect the requests.
