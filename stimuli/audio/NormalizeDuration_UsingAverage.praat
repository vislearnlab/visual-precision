
form NORMALIZE DURATION
	sentence Directory_to_read_from: /Users/vislearnlab/Documents/visual-precision/stimuli/audio/one_syllable
	sentence Directory_to_save: /Users/vislearnlab/Documents/visual-precision/stimuli/audio/normed/one_syllable
endform

desired_intensity = 65

#### everthing below is automated ####

# remove open files
clearinfo
select all
nocheck Remove

# create table to keep track of durations
results = Create Table with column names... Results 1  File ni 1 2 3 4 5 6 7 8 9

# get files in a directory
string = Create Strings as file list... files  'directory_to_read_from$'/*.wav
numberOfSounds = Get number of strings

# open all files, label, and get durations
for i to numberOfSounds
	select string
	file$ = Get string... i
	file'i'$ = file$
	file'i' = Read from file... 'directory_to_read_from$'/'file$'
	sentenceDuration'i' = Get total duration
	textGrid$ = directory_to_save$ + "/" + file$ - "wav" + "TextGrid"

	# check if TextGrid was already created
	if fileReadable(textGrid$)
		textGrid'i' = Read from file... 'textGrid$'
	else
		textGrid$ = directory_to_save$ + "/" + file$ - "wav" + "TextGrid"
		if fileReadable(textGrid$)
			textGrid'i' = Read from file... 'textGrid$'
		else
			textGrid'i' = To TextGrid... word 
		endif
	endif

	plus file'i'
	Edit
	pause Define the start and name of the label, close the Window, then press Continue
	select textGrid'i'
	ni = Get number of intervals... 1
	ni'i' = ni

	for interval to ni
		select textGrid'i'
		start'interval''i' = Get start point... 1 interval
		end'interval''i' = Get end point... 1 interval
		duration'interval''i' = end'interval''i'  - start'interval''i'
		column$ = "'interval'"
		select results
		duration = duration'interval''i'
		Set numeric value... i 'column$' duration'interval''i'
	endfor

	Set numeric value... i ni ni
	Set string value... i File 'file$'

	select textGrid'i'	
	textGrid$ = file'i'$ - ".wav" + ".TextGrid"
	Write to text file... 'directory_to_save$'/'textGrid$'

	select results
	if (i < numberOfSounds)
		Append row
	endif
endfor

Write to table file... 'directory_to_save$'/results.txt

ni = Get maximum... ni
printline Interval'tab$'mean duration
for interval to ni
	select results
	column$ = "'interval'"
	Extract rows where column (text)... 'column$' "is not equal to" 
	mean'interval' = Get mean... 'column$'
	meanTemp = mean'interval' * 1000
	printline 'interval''tab$''meanTemp:0'
endfor

for i to numberOfSounds
	ni = Table_Results[i, 2]
	select file'i'
	manipulation = To Manipulation... 0.01 75 600
	Extract duration tier

	for interval to ni
		durationRatio = mean'interval'/duration'interval''i'

		Add point... start'interval''i'+0.000000000001 durationRatio

		if interval = ni
			Add point... end'interval''i'-0.00000000001 durationRatio
		else
			Add point... end'interval''i' durationRatio
		endif
	endfor

	plus manipulation
	Replace duration tier
	select manipulation
	Get resynthesis (overlap-add)

	Scale intensity... 'desired_intensity'
	
	file$ = file'i'$
	Write to WAV file... 'directory_to_save$'/norm_'file$'

endfor

select all
minus results
Remove