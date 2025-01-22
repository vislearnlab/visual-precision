library(tidyverse)
library(rlang)

# Function to summarize whether a trial is usable based on whether the subject is looking at the screen for greater than 50% of the critical window
summarize_subj_usable_trials <- function(data, critical_window, suffix, additional_fields=NULL) {
  paste("hi")
  additional_fields <- additional_fields %||% list()
  
  data %>%
    filter(time_normalized_corrected >= critical_window[1] &
             time_normalized_corrected <= critical_window[2]) %>%
    group_by(SubjectInfo.subjID, Trials.trialID, Trials.ordinal, Trials.trialType) %>%
    summarize(
      length = n(),
      usable_frames = sum(not_looking_away, na.rm = TRUE),
      percent_usable = usable_frames / length,
      usable = ifelse(percent_usable >= 0.5, 1, 0), # usable if at least 50% looking
      mean_target_looking = mean(accuracy, na.rm = TRUE),
      !!!additional_fields,
    ) %>%
    rename_with(~ paste0(., "_", suffix), -c(SubjectInfo.subjID, Trials.trialID, Trials.ordinal, Trials.trialType))
}

# Function to compute whether a trial is usable based on whether both the critical window and the baseline window are usable
compute_usable_trial <- function(baseline_col, critical_col) {
  case_when(
    is.na(baseline_col) ~ 0,
    is.na(critical_col) ~ 0,
    baseline_col == 1 & critical_col == 1 ~ 1,
    TRUE ~ 0
  )
}

# Calculate mean, standard deviation, standard error and confidence intervals for data grouped across two variables
summarized_data <- function(data, x_var, y_var, group_var) {
  return(data |>
           group_by(across(all_of(c(x_var, group_var)))) |>
           summarize(
                   #across(everything(), ~ if (n_distinct(.) == 1) first(.) else NA),
                    mean_value = mean(.data[[y_var]], na.rm = TRUE),
                     sd_value = sd(.data[[y_var]], na.rm = TRUE),
                     N = n(),
                     se = sd_value / sqrt(n()),
                     ci=qt(0.975, N-1)*sd_value/sqrt(N),
                     lower_ci=mean_value-ci,
                     upper_ci=mean_value+ci,
                     .groups = 'drop') |>
           select(where(~ !all(is.na(.))))
  )
}

# make aesthetics aware size scale, also use better scaling
scale_size_c <- function(name = waiver(), breaks = waiver(), labels = waiver(), 
                         limits = NULL, range = c(1, 6), trans = "identity", guide = "legend", aesthetics = "size") 
{
  continuous_scale(aesthetics, "area", scales::rescale_pal(range), name = name, 
                   breaks = breaks, labels = labels, limits = limits, trans = trans, 
                   guide = guide)
}

# summarize target looking by input condition
summarize_data <- function(data,summary_field) {
  return(data  |>
           summarize(N=n(),
                     #mean_age = mean(age),
                     #mean_age_mo = mean(age_mo),
                     average_corrected_target_looking=mean(corrected_target_looking,na.rm=TRUE),
                     se=sd(corrected_target_looking,na.rm=T)/sqrt(N),
                     ci=qt(0.975, N-1)*sd(corrected_target_looking,na.rm=T)/sqrt(N),
                     lower_ci=average_corrected_target_looking-ci,
                     upper_ci=average_corrected_target_looking+ci,
                     lower_se=average_corrected_target_looking-se,
                     upper_se=average_corrected_target_looking+se,
                     average_critical_window_looking=mean(mean_target_looking_critical_window,na.rm=TRUE),
                     critical_window_ci = qt(0.975, N-1)*sd(mean_target_looking_critical_window,na.rm=T)/sqrt(N),
                     critical_window_lower_ci=average_critical_window_looking-critical_window_ci,
                     critical_window_upper_ci=average_critical_window_looking+critical_window_ci) |>
    rename_with(~ paste0(., "_", suffix), -c(SubjectInfo.subjID, Trials.trialID, Trials.ordinal, Trials.trialType)))
  }


#stolen from peekbank/ peekds
#https://github.com/langcog/peekds/blob/master/R/generate_aoi.R

resample_aoi_trial <- function(df_trial, sample_duration=1000/30) {
  
  print(paste0("Subject Number: ",unique(df_trial$sub_num), "; Trial Number: ", unique(df_trial$Trials.ordinal)))
  
  t_origin <- df_trial$t_norm
  data_origin <- df_trial$aoi
  
  # create the new timestamps for resampling
  t_start <- min(t_origin) - (min(t_origin) %% sample_duration)
  t_resampled <- seq(from = t_start, to = max(t_origin),
                     by = sample_duration)
  
  # exchange strings values with integers for resampling
  # this step critical for interpolating missing vals quickly and correctly
  aoi_num <- data_origin %>%
    dplyr::recode(target = 1, distractor = 2, other = 3, missing = 4)
  
  # start resampling with approx
  aoi_resampled <- stats::approx(x = t_origin, y = aoi_num, xout = t_resampled,
                                 method = "constant", rule = 2,
                                 ties = "ordered")$y
  aoi_resampled_recoded <- aoi_resampled %>%
    dplyr::recode("1" = "target", "2" = "distractor",
                  "3" = "other", "4" = "missing")
  
  
  # adding back the columns to match schema
  dplyr::tibble(t_norm = t_resampled,
                aoi = aoi_resampled_recoded,
                trial_id = df_trial$trial_id[1],
                administration_id = df_trial$administration_id[1])
}

resample_times <- function(df_table, sample_duration) {
  
  # first check if this data frame has all the correct columns required for
  # re-sampling
  required_columns <- c("trial_id", "administration_id", "t_norm", "aoi")
  
  # re-zero and normalize times first
  # this is mandatory, comes from our decision that not linking resampling and
  # centering causes a lot of problems
  if (!all(required_columns %in% colnames(df_table))) {
    stop(.msg("Resample times function requires the following columns to be
              present in the dataframe:
              {paste(required_columns, collapse = ', ')}. Times should be
              re-zeroed and normalized first before being resampled!"))
  }
  
  # main resampling call
  # start resampling process by iterating through every trial within every
  # administration
  df_out <- df_table %>%
    dplyr::mutate(admin_trial_id = paste(.data$administration_id,
                                         .data$trial_id, sep = "_")) %>%
    split(.$admin_trial_id) %>%
    purrr::map_df(resample_aoi_trial, sample_duration=sample_duration) %>%
    dplyr::arrange(.data$administration_id, .data$trial_id)
  
  return(df_out)
}

