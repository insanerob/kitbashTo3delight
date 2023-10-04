# kitbashTo3delight
Houdini - Python Converts Kitbash Cargo principled Materials to 3Delight Materials
this will convert to either the 3delight substance shader or the glass shader depending if it find a refraction texture

##Setup
###Add to Shelf
Right-click on the shelf and then New Tool
Options - set name and label, I call mine KB3D23DL
Script - Make sure the language is python and then paste in the context of the .py in the repo
.. apply, accept.

##Use
###Convert Materials
Select the /obj node containing your kitbash model and its matnet (after importing it from Kitbash3D Cargo
Click the tool you created.
It will now look for all principled shaders within that node and convert them to a new node /obj/3dlmatnet which contains the 3delight materials

###Update Material references
In the kitbash object node add a  Primivite Wrangle node before the Output node.
Add this vex (example for Hong Kong kit, change the KB3D_HOK to your node name e.g. '/obj/KB3D_AOE/matnet' for Egypt kit )

@shop_materialpath = replace(s@shop_materialpath , '/obj/KB3D_HOK/matnet' , '/obj/3dlmatnet') ;
@shop_materialpath += "/dlTerminal1" ;

.. Restart the viewport render so the new materials are used.

.. let me know if you find any issues with materials

rOb :)
