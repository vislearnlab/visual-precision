library(tidyverse)
library(rlang)
library(gghalves)
library(ggh4x)

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
  
  #print(paste0("Subject Number: ",unique(df_trial$sub_num), "; Trial Number: ", unique(df_trial$Trials.ordinal)))
  
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

add_aoa_split <- function(data) {
  data |>
    mutate(mean_aoa = mean(AoA_Est_target),
           aoa_half = ifelse(AoA_Est_target > mean(AoA_Est_target), "higher", "lower"))
}

half_violins_plot <- function(data, x_var, y_var, group_var, violin_conditions, input_xlab="Distractor Difficulty Condition",
                              input_ylab="Baseline-Corrected\nProportion Target Looking",input_caption="") {
  jitterer <- position_jitter(width = .05,seed=1)
  avg_corrected_target_looking <- summarized_data(data, x_var, y_var, group_var) |> filter(N > 5)
  
  overall_corrected_target_looking <- summarized_data(avg_corrected_target_looking |>
                                        rename(avg_corrected_target_looking = mean_value), x_var, "avg_corrected_target_looking", x_var)
  
  overall_corrected_target_looking %>%
    knitr::kable()
  
  set.seed(2)
  
  overall_condition_plot <- ggplot(avg_corrected_target_looking, aes(x=.data[[x_var]], y=mean_value, fill=.data[[x_var]])) +
    gghalves::geom_half_violin(data=filter(avg_corrected_target_looking, .data[[x_var]]==violin_conditions[[1]]), 
                               position=position_nudge(x=-.1, y=0), width=1, trim=FALSE, alpha=.8, 
                               color=NA, side="l", fill="#77DD77") +  # Pastel green
    gghalves::geom_half_violin(data=filter(avg_corrected_target_looking, .data[[x_var]]==violin_conditions[[2]]), 
                               position=position_nudge(x=.1, y=0), width=1, trim=FALSE, alpha=.8, 
                               color=NA, side="r", fill="#FF6961") +  # Pastel red
    geom_path(aes(group=SubjectInfo.subjID), color="black", fill=NA, alpha=0.15, size=0.75, position=jitterer) +   
    geom_point(aes(color=.data[[x_var]], group=SubjectInfo.subjID), size=2.5, alpha=0.15, position=jitterer) +
    geom_point(data=overall_corrected_target_looking, aes(y=mean_value), color="black", size=5) +
    geom_line(data=overall_corrected_target_looking, aes(y=mean_value, group=1), color="black", size=3) +
    geom_errorbar(data=overall_corrected_target_looking, aes(y=mean_value, ymin=lower_ci, ymax=upper_ci), width=0, size=1.2, color="black") +
    geom_hline(yintercept=0, linetype="dashed") +
    scale_color_manual(values = setNames(c("#77DD77", "#FF6961"), 
                                         as.character(sapply(violin_conditions, sym)))) +# Match point colors
    theme(legend.position="none") +
    xlab(input_xlab) +
    ylab(input_ylab) +
    labs(title="", caption = input_caption) +
    theme(axis.title.x = element_text(face="bold", size=20),
          axis.text.x  = element_text(size=14),
          axis.title.y = element_text(face="bold", size=20),
          axis.text.y  = element_text(size=16),
          strip.text.x = element_text(size=16, face="bold"))
}

similarity_effect_plot <- function(data, x_var, y_var="mean_value", model_type) {
  sim_type <- strsplit(x_var, "_")[[1]][1]
  ggplot(data, aes(x = .data[[x_var]], y = .data[[y_var]])) +
    geom_hline(yintercept=0,linetype="dashed")+
    geom_point(size = 3, alpha = 0.5) +
    geom_linerange(aes(ymin = .data[[y_var]] - ci, ymax = .data[[y_var]] + ci), alpha = 0.1) + 
    geom_smooth(method = "lm") +
    geom_label_repel(aes(label = paste(Trials.targetImage, "-", Trials.distractorImage)), max.overlaps = 5) +
    ylab("Baseline-corrected proportion target looking") +
    xlab(paste(model_type,"target-distractor",sim_type,"similarity")) +
    ggpubr::stat_cor(method = "spearman")
}

multiple_similarity_effects_plot <- function(data, x_var, y_var="mean_value", group_var, input_title) {
  sim_type <- strsplit(x_var, "_")[[1]][1]
  label_data <- data %>% 
    filter(Trials.targetImage == "bulldozer" | Trials.distractorImage == "bulldozer") %>%
    mutate(label = paste("Target:", Trials.targetImage, "\nDistractor:", Trials.distractorImage))
  
  ggplot(data, aes(x = .data[[x_var]], y = .data[[y_var]])) +  # Removed color from aes()
    geom_hline(yintercept = 0, linetype = "dashed") +
    geom_point(size = 8, alpha = 0.5, color = "#215D89") +  # Set color outside aes()
    geom_smooth(alpha = 0.3, size = 0, method = "lm", show.legend = F, color = "#215D89") +  # Set color outside aes()
    stat_smooth(geom = "line", alpha = 0.9, size = 1.5, method = "lm", show.legend = F, color = "#215D89") +  # Set color outside aes()
    coord_cartesian(ylim = c(-0.12, 0.22)) +
    geom_label_repel(
      data = label_data,
      aes(label = label),
      segment.alpha = 0.7,
      nudge_y = ifelse(label_data$Trials.targetImage == "bulldozer", -0.02, 0.02),
      force = 10,
      force_pull = 0.1,
      size = 6,
      segment.size = 1.2,
      point.padding = unit(1, "lines"),
      min.segment.length = 0,
      box.padding = unit(0.5, "lines"),
      max.overlaps = Inf,
      label.padding = unit(0.25, "lines"),
      label.r = unit(0.5, "lines"),
      show.legend = FALSE
    )+
    ylab("Baseline-corrected\nproportion target looking") +
    xlab("Target-distractor embedding similarity") +
    #scale_x_continuous(breaks = seq(0.5, 0.9, by = 0.1)) +
    scale_y_continuous(breaks = seq(-0.1, 0.2, by = 0.1)) +
    #ggthemes::theme_few() +
    theme_minimal()+
    theme(
      text = element_text(size = 16, face = "bold"),
      axis.title.x = element_text(
        face = "bold", 
        size = 29,
        margin = margin(t = 15, r = 0, b = 0, l = 0)
      ),
      legend.key = element_blank(),
      axis.title.y = element_text(
        face = "bold", 
        size = 29,
        margin = margin(t = 0, r = 10, b = 0, l = 0)
      ),
      axis.text = element_text(size = 24, face = "bold"),
      legend.title = element_text(size = 22, face = "bold"),
      legend.text = element_text(size = 22, face = "bold"),
      legend.position = "bottom",
      strip.text = element_text(size = 28, face = "bold"),
      strip.background = element_rect(fill = "gray90", color = NA),
      strip.text.x = element_text(margin = margin(t = 8, b = 8)), # Increase padding within strip
      panel.spacing = unit(0.5, "cm")
      #strip.placement = "top"# Adjust facet label size
    ) +
    facet_wrap(facets=~ .data[[group_var]],dir="v", strip.position="top", labeller = as_labeller(c("image_similarity" = "Image Similarity", "text_similarity" = "Text Similarity")),
               ncol=1, scales = "free")  +
    facetted_pos_scales(
      x = list(
        image_similarity = scale_x_continuous(
          breaks = seq(0.5, 0.9, by = 0.1),
          limits = c(0.43, 0.85)
        ),
        text_similarity = scale_x_continuous(
          breaks = seq(0.7, 0.9, by = 0.05),
          limits = c(0.7, 0.91)
        )
      )
    )
}

similarity_age_half_plot <- function(data, x_var, y_var="mean_value", group_var="age_half",model_type) {
  sim_type <- strsplit(x_var, "_")[[1]][1]
  ggplot(data, aes(x = .data[[x_var]], y = .data[[y_var]], color = .data[[group_var]])) +
    geom_hline(yintercept=0,linetype="dashed")+
    geom_point(size = 3, alpha = 0.5) +
    geom_smooth(method = "lm") +
    geom_linerange(aes(ymin = .data[[y_var]] - ci, ymax = .data[[y_var]] + ci), alpha = 0.1) + 
    scale_color_brewer(palette = "Set1", name="Age half") +  # Using RColorBrewer for colors
    ylab("Baseline-corrected proportion target looking") +
    xlab(paste(model_type,"target-distractor",sim_type,"similarity")) +
    ggpubr::stat_cor(method = "spearman") +
    labs(caption=paste0("Labels are in the order of target-distractor. M=",mean_age," months"))
}

age_half_plot <- function(data, x_var, y_var="mean_value", group_var="age_half", x_label, y_label="Baseline-corrected proportion target looking", labels=c(), title="") {
  sim_type <- strsplit(x_var, "_")[[1]][1]
  ggplot(data, aes(x = .data[[x_var]], y = .data[[y_var]], color = .data[[group_var]])) +
    geom_hline(yintercept=0,linetype="dashed")+
    geom_point(size = 3, alpha = 0.5) +
    geom_smooth(method = "lm") +
    geom_linerange(aes(ymin = .data[[y_var]] - ci, ymax = .data[[y_var]] + ci), alpha = 0.1) + 
    scale_color_brewer(palette = "Set1", name="Age half") +  # Using RColorBrewer for colors
    ylab("Baseline-corrected proportion target looking") +
    xlab(x_label) +
    ggpubr::stat_cor(method = "spearman") +
    labs(caption=paste0("M=",mean_age," months"), title=title)
}

epoch_age_half_plot <- function(data, x_var) {
  sim_type <- strsplit(x_var, "_")[[1]][1]
  
  ggplot(data, aes(x = epoch, y = pearson_cor, color = age_half)) +
    geom_hline(yintercept = 0, linetype = "dashed") +
    geom_point(size = 3) +  # Apply jitter to points only
    geom_errorbar(data = data[(data$epoch %% 7 == 0 & data$age_half == "younger") | 
                                (data$epoch %% 5 == 0 & data$age_half == "older"), ], 
                  aes(ymin = ci_lower, ymax = ci_upper), 
                  width = 0.3, alpha = 0.5) +  # No jitter on error bars
    geom_smooth(span = 2) +
    labs(title = paste(sim_type, "similarity correlation across Open-CLIP training"),
         x = "Epoch",
         y = "Coefficient of similarity") +  
    theme_minimal() +
    guides(shape = "none") +
    scale_color_brewer(palette = "Set1", name = "Age half") 
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

