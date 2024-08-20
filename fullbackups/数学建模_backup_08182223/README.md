./gpxfiles for processing
./gpsfix contains a couple of route whose gpx files differ and can only be processed with gpstracks data, processed by math_analyze_bugfix
./gpxroutes_originally_gpxfiles contains gpx route files (with time data) downloaded directly from AllTrails
./gpxtracks contains gpx track files (with accurate height data but no time data) downloaded directly from AllTrails
./merged_csv is nonsense, a killed version of premerge for files
./merged_gpx contains merged (accurate height & time data) gpx files, merged by mergedata.py
./output_history contains some historic versions of RESULTs but not that successful because of some reasons
./RESULT contains output data (guess if it's final data)
./reusable_files contains rubbish
final_calculation.py is used for calculate final winners (generates trail_energy_analysis.txt in ./RESULT)
debug.py is chatgpt's mind rubbish
math_analyze.py is the main program which analyze the ./gpxfiles and make csv files.
math_analyze_bugbix pls goto ./gpsfix
mergedata.py pls goto ./merged_gpx

Credit: @JerryJiang12923
蒋宇皓