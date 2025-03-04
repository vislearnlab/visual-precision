% Helper Function: Detect Object in Region
function bbox = detect_object(img, gray_mask, region_mask, region_name)
    % Extract image dimensions
    [imgH, imgW, ~] = size(img);
    
    % Mask for the specific region (left or right half)
    region_mask = region_mask & (~gray_mask); % Avoid gray areas
    
    % Get bounding box for the object
    stats = regionprops(region_mask, 'BoundingBox');
    if ~isempty(stats)
        bbox = stats(1).BoundingBox; % Detected bounding box
    else
        warning('%s not detected. Using estimated bounding box.', region_name);
        % Estimate bounding box if the object is not detected
        if strcmp(region_name, 'Left')
            bbox = [round(imgW * 0.1), round(imgH * 0.3), round(imgW * 0.3), round(imgH * 0.4)];
        elseif strcmp(region_name, 'Right')
            bbox = [round(imgW * 0.6), round(imgH * 0.3), round(imgW * 0.3), round(imgH * 0.4)];
        end
    end
end

% Helper Function: Extract Saliency values from Bounding Box
function [mean_saliency, max_saliency, sd_saliency] = extract_saliency(saliency_map, bbox)
    x_start = round(bbox(1));
    x_end   = round(bbox(1) + bbox(3));
    y_start = round(bbox(2));
    y_end   = round(bbox(2) + bbox(4));
    
    % Extract saliency in detected bounding box
    saliency_region = saliency_map(y_start:y_end, x_start:x_end);
    
    % Compute mean saliency for the region
    mean_saliency = mean(saliency_region(:));
    max_saliency = max(saliency_region(:));
    sd_saliency = std(saliency_region(:));
end

% Helper Function: Draw Bounding Boxes
function saved_image = draw_bboxes(img, saliency_map, left_bbox, right_bbox, saliency_data, title_text)
    if nargin < 6
        title_text = "Saliency Map";
    end
    fig = figure;

    %set(gca, 'Position', [0.05, 0.15, 0.9, 0.7]);
    %set(gca, 'OuterPosition', [0,0,1,1])
    %set(gca, 'LooseInset', [0,0,0,0]);
    hm = heatmap_overlay( img , saliency_map );
    imshow(hm, []);
    set(gca, 'Position', [0, 0, 1, 0.8]);
    hold on;
    %hAx=gca;
    %hAx.Position=hAx.Position.*[1 1 1 0.95];

    % Add text in the middle of the image
     % Add text at the top of each bounding box
    text(left_bbox(1) + left_bbox(3)/2, left_bbox(2) - 150, ...
        sprintf('Max: %.3f | Mean: %.3f', saliency_data.MaxTargetSaliency, saliency_data.MeanTargetSaliency), ...
        'Color', 'black', 'FontSize', 30, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');

    text(right_bbox(1) + right_bbox(3)/2, right_bbox(2) - 150, ...
        sprintf('Max: %.3f | Mean: %.3f', saliency_data.MaxDistractorSaliency, saliency_data.MeanDistractorSaliency), ...
        'Color', 'black', 'FontSize', 30, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');
    title(sprintf('%s | Mean Salience Diff: %.4f', title_text, saliency_data.MeanTargetSaliency - saliency_data.MeanDistractorSaliency), 'FontSize', 40);
    % Overlay bounding boxes on the saliency map
    rectangle('Position', left_bbox, 'EdgeColor', 'r', 'LineWidth', 2);
    rectangle('Position', right_bbox, 'EdgeColor', 'b', 'LineWidth', 2);
    frame = getframe(fig); 
    [saved_image, ~] = frame2im(frame);
    %close(fig)
end

% Helper Function: Compare Saliency for Different Image-Saliency Pairs with Default Values
function [saved_img, saliency_data] = compare_saliency(img, saliency_map, title_text, gray_mask, region_name_left, region_name_right)
    % Set default values for inputs if not provided
    if nargin < 5
        region_name_left = 'Left';
    end
    if nargin < 6
        region_name_right = 'Right';
    end
    if nargin < 4 || isempty(gray_mask)
        % Default gray_mask calculation
        hsv_img = rgb2hsv(img);
        H = hsv_img(:,:,1); % Hue
        S = hsv_img(:,:,2); % Saturation
        V = hsv_img(:,:,3); % Brightness (Value)
        gray_mask = (H < 0.05) & (S < 0.3) & (V > 0.4); % Low saturation and high brightness: expecting HSV (0, 2.94%, 53.33%)
    end
    if nargin < 3 || isempty(title_text)
        title_text = "Saliency Map";
    end
    if nargin < 2 || isempty(saliency_map)
        % Default saliency map calculation
        out_gbvs = gbvs(img);
        saliency_map = out_gbvs.master_map_resized;
    else
        saliency_map = imresize(saliency_map, [size(img, 1), size(img, 2)]);
    end
    
    % Extract image dimensions
    [imgH, imgW, ~] = size(img);

    % Define region masks for left and right
    left_half = 1:round(imgW/2);
    left_region = false(imgH, imgW);
    left_region(:, left_half) = true; % Only consider the left half
    
    right_half = round(imgW/2):imgW;
    right_region = false(imgH, imgW);
    right_region(:, right_half) = true; % Only consider the right half
    
    % Detect bounding boxes for left and right regions
    left_bbox = detect_object(img, gray_mask, left_region, region_name_left);
    right_bbox = detect_object(img, gray_mask, right_region, region_name_right);
    
    % Extract saliency values from detected regions
    [mean_saliency_left, max_saliency_left, sd_saliency_left] = extract_saliency(saliency_map, left_bbox);
    [mean_saliency_right, max_saliency_right, sd_saliency_right] = extract_saliency(saliency_map, right_bbox);
    saliency_data = table(mean_saliency_left, max_saliency_left, sd_saliency_left, ...
                         mean_saliency_right, max_saliency_right, sd_saliency_right, ...
                         'VariableNames', {'MeanTargetSaliency', 'MaxTargetSaliency', 'SDTargetSaliency', ...
                                         'MeanDistractorSaliency', 'MaxDistractorSaliency', 'SDDistractorSaliency'});  
    % Display results
    saved_img = draw_bboxes(img, saliency_map, left_bbox, right_bbox, saliency_data, title_text);
    hold on;
end

% Create output table to store saliency metrics
% Read PROJECT_PATH from environment file
D = loadenv('.env');
PROJECT_PATH = D("PROJECT_PATH");
disp(PROJECT_PATH);

% Read image pairs data
% Read image pairs data
image_pairs = readtable(fullfile(PROJECT_PATH, 'data/metadata/level-imagepair_data.csv'));

% Create output table for saliency metrics
metrics = {'ImagePair', 'MeanTargetSaliency', 'MaxTargetSaliency', 'SDTargetSaliency', ...
           'MeanDistractorSaliency', 'MaxDistractorSaliency', 'SDDistractorSaliency'};

saliency_metrics = table('Size', [height(image_pairs), 8], ...
    'VariableTypes', {'string', 'double', 'double', 'double', 'double', 'double', 'double', 'double'}, ...
    'VariableNames', [metrics, {'MeanSaliencyDiff'}]);

for i = 1:height(image_pairs)
    img_pair = strcat(image_pairs.Word1{i}, '-', image_pairs.Word2{i});
    disp(img_pair)
    img = imread(fullfile(PROJECT_PATH, 'experiment', 'frames', strcat(img_pair, '.png')));
    [~, saliency_data] = compare_saliency(img);
    
    saliency_metrics.ImagePair(i) = string(img_pair);
    for m = metrics(2:end)
        saliency_metrics.(m{1})(i) = round(saliency_data.(m{1}), 4);
    end
    saliency_metrics.MeanSaliencyDiff(i) = round(saliency_metrics.MeanTargetSaliency(i) - saliency_metrics.MeanDistractorSaliency(i), 4);
end

% Save saliency metrics to CSV
writetable(saliency_metrics, fullfile(PROJECT_PATH, 'data', 'metadata', 'level-imagepair_added-saliency_data.csv'));

% broken down saliency maps 
% img = imread("/path/to/image")
%[saved_img] = compare_saliency(img, out_gbvs.master_map_resized);
%[saved_img_dklcolor] = compare_saliency(img, out_gbvs.top_level_feat_maps{1,1}, "DKL Color map");
%[saved_img_intensity] = compare_saliency(img, out_gbvs.top_level_feat_maps{1,2}, "Intensity map");
%[saved_img_orientation] = compare_saliency(img, out_gbvs.top_level_feat_maps{1,3}, "Orientation map");
%close all;
%concatenated = cat(1, saved_img, saved_img_dklcolor, saved_img_intensity, saved_img_orientation);
%imshow(concatenated)