library(tidyverse)
library(rlang)


# Function to summarize whether a trial is usable based on whether the subject is looking at the screen for greater than 50% of the critical window
summarize_subj_usable_trials <- function(data, critical_window, suffix, additional_fields=NULL) {
  additional_fields <- additional_fields %||% list()
  
  data %>%
    filter(time_normalized_corrected >= critical_window[1] &
             time_normalized_corrected <= critical_window[2]) %>%
    group_by(SubjectInfo.subjID, Trials.trialID, Trials.ordinal, Trials.trialType) %>%
    summarize(
      length = n(),
      useable_frames = sum(not_looking_away, na.rm = TRUE),
      percent_usable = useable_frames / length,
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

# Function to add age split
add_age_split <- function(data) {
  data |>
    mutate(
      mean_age = mean(SubjectInfo.testAge) / 30,
      age_half = ifelse(SubjectInfo.testAge > mean(SubjectInfo.testAge), "older", "younger")
    )
}

similarity_effect_plot <- function(data, x_var, y_var="mean_value", model_type) {
  sim_type <- strsplit(x_var, "_")[[1]][1]
  ggplot(data, aes(x = .data[[x_var]], y = .data[[y_var]])) +
    geom_hline(yintercept=0,linetype="dashed")+
    geom_point(size = 3, alpha = 0.5) +
    geom_linerange(aes(ymin = .data[[y_var]] - ci, ymax = .data[[y_var]] + ci), alpha = 0.1) + 
    geom_smooth(method = "lm") +
    geom_label_repel(aes(label = paste(Trials.targetImage, "-", Trials.distractorImage)), max.overlaps = Inf) +
    ylab("Baseline-corrected proportion target looking") +
    xlab(paste(model_type,"target-distractor",sim_type,"similarity")) +
    ggpubr::stat_cor(method = "spearman")
}

similarity_age_half_plot <- function(data, x_var, y_var="mean_value", group_var="age_half",model_type) {
  sim_type <- strsplit(x_var, "_")[[1]][1]
  ggplot(data, aes(x = .data[[x_var]], y = .data[[y_var]], color = .data[[group_var]])) +
    geom_hline(yintercept=0,linetype="dashed")+
    geom_point(size = 3, alpha = 0.5) +
    geom_smooth(method = "lm") +
    geom_linerange(aes(ymin = .data[[y_var]] - ci, ymax = .data[[y_var]] + ci), alpha = 0.1) + 
    scale_color_brewer(palette = "Set2", name="Age half") +  # Using RColorBrewer for colors
    ylab("Baseline-corrected proportion target looking") +
    xlab(paste(model_type,"target-distractor",sim_type,"similarity")) +
    ggpubr::stat_cor(method = "spearman") +
    labs(caption=paste0("Labels are in the order of target-distractor. M=",mean_age," months"))
}

epoch_age_half_plot <- function(data, x_var) {
  sim_type <- strsplit(x_var, "_")[[1]][1]
  ggplot(data, aes(x = epoch, y = pearson_cor, color = age_half)) +
    geom_point(aes(shape = p_value < 0.05), size = 3) + 
    geom_smooth(span = 2) +
    labs(title = paste(sim_type, "similarity correlation across Open-CLIP training"),
         x = "Epoch",
         y = "Coefficient of similarity") +  # Set color for significance
    theme_minimal() +
    guides(shape = "none") +
    scale_color_brewer(palette = "Set2", name="Age half") 
}

summarize_similarity_data <- function(data, extra_fields=NULL) {
  group_vars = c("Trials.trialID", "Trials.targetImage", "Trials.distractorImage", "image_similarity", "cor")
  if ("text_similarity" %in% colnames(data)) {
    group_vars = c(group_vars, "text_similarity", "multimodal_similarity")
  }
  if (!is.null(extra_fields)) {
    group_vars = c(group_vars, extra_fields)
  }
  return(summarized_data(
    data,
    "Trials.trialID", 
    "corrected_target_looking", 
    group_vars
  ))
}

# To add a title to the top of a cowplot arrangement
cowplot_title <- function(title_text) {
  title <- ggdraw() + 
    draw_label(
      title_text,
      fontface = 'bold',
      x = 0,
      hjust = 0
    ) +
    theme(
      plot.margin = margin(0, 0, 0, 4)
    )
  return(title)
}

# Function to generate plots correlating looking time with image pair similarities across vision, language and text correlations. Accounts for models
# that are missing one or more of those values
generate_multimodal_plots <- function(data, model_type, suffix = "") {
  # Initialize an empty list to store the plots
  plot_list <- list()
  
  # Conditionally add plots for existing columns
  for (col in c("text_similarity", "image_similarity", "multimodal_similarity")) {
    if (col %in% colnames(data)) {
      plot_list[[length(plot_list) + 1]] <- similarity_effect_plot(data, paste0(col, suffix), "mean_value", model_type)
    }
  }
  
  # Create the combined plot grid
  plots <- cowplot::plot_grid(plotlist = plot_list, nrow = 2)
  
  # Add the title
  title <- cowplot_title(paste0("Target looking and semantic similarity correlations for ", model_type))
  
  # Combine the title and the plots into one grid
  grid <- cowplot::plot_grid(title, plots, rel_heights = c(0.2, 1), ncol = 1)
  
  # Save the plot
  cowplot::save_plot(here("figures", PROJECT_VERSION, paste0(model_type, "_similarities.png")), grid, base_width = 10, base_height = 12, bg = "white")
  
  # Return the grid
  grid
}


# Function to generate plots correlating the looking time of infants across two age groups with image pair similarities across vision, language and text correlations
generate_multimodal_age_effect_plots <- function(data, model_type, suffix = "") {
  # Initialize an empty list to store the plots
  plot_list <- list()
  
  # Conditionally add plots for existing columns
  for (col in c("text_similarity", "image_similarity", "multimodal_similarity")) {
    if (col %in% colnames(data)) {
      plot_list[[length(plot_list) + 1]] <- similarity_age_half_plot(data, x_var=paste0(col, suffix), model_type=model_type)
    }
  }
  
  # Create the combined plot grid
  plots <- cowplot::plot_grid(plotlist = plot_list, nrow = 2)
  title <- cowplot_title(paste0("Target looking and semantic similarity correlations by age for ", model_type))
  grid <- cowplot::plot_grid(title, plots, rel_heights = c(0.2, 1), ncol=1)
  cowplot::save_plot(here("figures",PROJECT_VERSION,paste0(model_type,"_age_similarities.png")), grid, base_width = 10, base_height = 12, bg="white")
  grid
}

# Create correlational and age-split plots for a model 
create_model_plots <- function(input_similarities, name="CVCL") {
  similarities_combined <- input_similarities |>
    rename(word_a = word1, word_b = word2) |>
    bind_rows(
      input_similarities |>
        rename(word_a = word2, word_b = word1)
    )
  
  looking_data_w_model <- looking_data_summarized |>
    select(-text_similarity, -multimodal_similarity, -image_similarity) |>
    left_join(similarities_combined, by = c("Trials.distractorImage"="word_a", "Trials.targetImage"="word_b"))
  
  data_summarized <- summarize_similarity_data(looking_data_w_model)
  
  age_half_summarized <- looking_data_w_model |>
    add_age_split() |>
    summarize_similarity_data(extra_fields = c("age_half"))
  
  generate_multimodal_plots(data_summarized, name)
  generate_multimodal_age_effect_plots(age_half_summarized, model_type=name)
}

