library(dplyr)
library(wordbankr)
library(tools)

# To save a frame list base to be randomized and completed in Lookit
save_frame_list <- function(stimuli, file_path) {
  image_list <- list()
  for (i in 1:nrow(stimuli)) {
    image_frame <- tibble(
      id = c(paste(stimuli$item_pair[i], "left",sep="-"),paste(stimuli$item_pair[i],"right",sep="-")), 
      src = sample(c(stimuli$Image_Word1[i], stimuli$Image_Word2[i])),
      position = c("left", "right"))
    image_list[[i]] <- image_frame
  }
  frame_list_base <- tibble(
    audio = file_path_sans_ext(stimuli$Audio_File_Word_1),
    images = image_list,
    id = paste(stimuli$wordPairing, stimuli$item_pair, sep="-")
  )
  frame_list_distractor <- tibble(
    audio = file_path_sans_ext(stimuli$Audio_File_Word_2),
    images = image_list,
    id = paste(stimuli$wordPairing, stimuli$item_pair, "distractor", sep="-")
  )
  all_frames <- bind_rows(frame_list_base, frame_list_distractor)
  #all_frames <- frame_list_base
  save_stimuli(c(stimuli$Audio_File_Word_1, stimuli$Audio_File_Word_2), image_list)
  frame_list_json <- toJSON(all_frames,pretty=TRUE)
  write(frame_list_json, file_path)
  return(all_frames)
}

# Move relevant stimuli from the existing older stimuli directory to the new path designed for Lookit unless they already exist there
save_stimulus <- function (source_path, dest_path, file) {
  if (!file.exists(file.path(dest_path, file))) {
    file.copy(file.path(source_path, file), file.path(dest_path, file))
  }
}

save_stimuli <- function(audio, images) {
  for (i in seq_along(images)) {
    save_stimulus(SOURCE_IMAGES_PATH, DEST_IMAGES_PATH, images[[i]]$src[1])
    save_stimulus(SOURCE_IMAGES_PATH, DEST_IMAGES_PATH, images[[i]]$src[2])
  }
  for (i in seq_along(audio)) {
    save_stimulus(SOURCE_AUDIO_PATH, DEST_AUDIO_PATH, audio[i])
  }
}

# To convert recognizability ratings from Things+ to the right format
cleaned_recognizability_rating <- function(x) {
      parts <- unlist(strsplit(x, "\\."))
       if (length(parts) >= 3) {
             return(paste0("0.", parts[1]))  # For "X.Y.Z", return "0.X"
         } else if (as.numeric(x) > 1) {
           return(paste0("0.", paste(parts, collapse="")))  # For "A.B" or "C.D", return "0.B" or "0.D" where A and C are greater than 1
       } else { return(x) }
}

# To extract data about the age-of-acquisition (AoA) of words using Wordbank
aoa_data <- function(language, form, input_measure) {
  instrument_data <- get_instrument_data(language, form, administration_info = TRUE) |>
    filter(!is.na(!!sym(input_measure)))
  aoa <- merge(x=fit_aoa(instrument_data, measure=input_measure),y=get_item_data(language, form),by="item_id") |> 
    filter(!is.na(aoa)) |>
    # Only using the first phrase of the description
    mutate(item = str_extract(item_definition, "^[^/()]+")) |>
    # Only count the AoA as the last learned date of that word if there are multiple versions of the word
    filter(aoa == max(aoa, na.rm = TRUE), .by=item)
}

# To optionally merge the AoAs from Wordbank with an experimental stimuli dataset
merged_aoas <- function(existing_stimuli, aoa_data) {
  return(existing_stimuli %>%
           left_join(aoa_data[,c("item", "aoa")], by=c("Word1" = "item")) %>%
           rename(AoA_Word1_WB = aoa) %>%
           left_join(aoa_data[,c("item", "aoa")], by=c("Word2" = "item")) %>%
           rename(AoA_Word2_WB = aoa)
         )
}

# To merge the older existing stimuli data with new correlation and AoA data 
merged_stimuli <- function(existing_stimuli, aoa_data) {
  return(existing_stimuli %>%
    inner_join(aoa_data, by = c("Word1" = "item")) %>%
    rename(AoA_Word1_WB = aoa)) #%>%
    #inner_join(aoa_data, by = c("Word2" = "item")) %>%
    #rename(AoA_Word2_WB = aoa) %>%
    #mutate(aoa_diff_wb = (AoA_Word1_WB - AoA_Word2_WB)/12))
}

