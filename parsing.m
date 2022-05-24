% Converts .xls files with course info to .json file
% Running instructions: place this file in the same folder as parseExcel.m
% and the Excel sheets containing all the course data. These Excel 
% files must be named "RO_COURSES_BY_DEPT_OR_FACULTY_DEPT.xls".
% where DEPT is the department name (seen below).
% Run this script in Matlab. A new file will be created called parsed.json
% in the same folder. This will contain all of the course data from the Excel
% files.
%
% Author: Zachary Schmidt, UAlberta, Summer 2022

in_file_engg = "RO_COURSES_BY_DEPT_OR_FACULTY_ALL_ENG.xls";
out_stream = parseExcel(in_file_engg);

out_file = "parsed.json";
fid = fopen(out_file, "w");
fprintf(fid, out_stream);

in_file_chem = "RO_COURSES_BY_DEPT_OR_FACULTY_CHEM.xls";
out_stream = parseExcel(in_file_chem);
fprintf(fid, out_stream);

in_file_engl = "RO_COURSES_BY_DEPT_OR_FACULTY_ENGLISH.xls";
out_stream = parseExcel(in_file_engl);
fprintf(fid, out_stream);

in_file_math = "RO_COURSES_BY_DEPT_OR_FACULTY_MATH.xls";
out_stream = parseExcel(in_file_math);
fprintf(fid, out_stream);

in_file_phys = "RO_COURSES_BY_DEPT_OR_FACULTY_PHYSICS.xls";
out_stream = parseExcel(in_file_phys);
fprintf(fid, out_stream);

fclose("all");