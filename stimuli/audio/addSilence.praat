# created on 3/15/15 by Ron Pomper

# this script concatenates the normed targets (e.g., "Where's the dog?") 
# and attention getters ("That's cool!") inserting silence before, between, and afterwards

# the script is written such that it will combine a selected attention getter (ag$) with every target

# note: in order to work, both the files for the targets and AGs must have "norm_" appended 
# to the front of each file name (e.g., "norm_dog.aiff"). the script removes the "norm_" text
# when exporting the concatenated file in WAV format

# specify the directory paths 
directory_for_targets$ = "/Users/vislearnlab/Documents/visual-precision/stimuli/audio/looks"
directory_to_save$ = "/Users/vislearnlab/Documents/visual-precision/stimuli/audio/looks/with_silence"

# select the AG you want
#ag$ = "cool2"

# enter the amount of silence to occur: 
# before sound onset, 
# between the target sentence and attention getter &
# after the offset of sound

before$ = "0.12"
#between$ = "0.2"
after$ = "0"

#string = Read Strings from raw text file... 'directory_for_targets$'/labelList.txt

#### everything below is automated ####

# get files in the to read directory
string = Create Strings as file list... files  'directory_for_targets$'/*.wav
numberOfSounds = Get number of strings
print numberOfSounds
# open all files and save durations, pitches, and intensities to table
for i to numberOfSounds
	Create Sound from formula: "silence_before", 1, 0, 'before$', 44100, "0"
	select string
	file$ = Get string... i
	file'i' = Read from file... 'directory_for_targets$'/'file$'
	name$ = "'file$'" - ".wav"
	#Create Sound from formula: "silence_between", 1, 0, 'between$', 44100, "0"
	#Read from file... 'directory_for_AG$'/norm_'ag$'.aiff
	#Create Sound from formula: "silence_after", 1, 0, 'after$', 44100, "0"
	select all
	minus Strings files
	Concatenate
	Write to WAV file... 'directory_to_save$'/'name$'.wav
	select all
	minus Strings files
	Remove
endfor

select all
Remove
