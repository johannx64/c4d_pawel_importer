# c4d_pawel_importer
 custom material importer for C4D
I got one request.
You've made that batch imports FBXs & sets up the materials accoriding to our needs. (it converts materials for People & Accessories as well).



Right now we've introduced new type of models called Posed Plus. They also have 3d Hair (made with haircards).
a) The Hair have separate material (that shold have connected following maps: Color, Specular, Roughness, Normal & Alpha - it doesnt work now)(it follows same naming scheme like Accessories).
b) Now also the Human material has Alpha map - that should be assigned to human material (like for accessories)
c) both Human & Hair have now also Ambient Occlusion maps - these should be mixed with Color maps with multiply mode (0,3 value / 30%)



All of this should be set like before - just adding use of Hair material (like accessories) and add use of Ambien Occlusion Maps (for Hair & Human)



See the attachted materials, I also attach 2 sample models to test the script on.
Let me know time line and budget for this fix.