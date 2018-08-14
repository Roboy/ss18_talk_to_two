close all;

do_pdm_stuff = 0;
do_scale_stuff = 0;
do_get_rid = 1;
do_rid_pdm_stuff = 1;
f_s = 3072000;
f_c = 8e3;
bit_width = 24;
lpfilter = designfilt('lowpassiir', 'PassbandFrequency', f_c, 'StopbandFrequency', 15e3, 'PassbandRipple', 1, 'StopbandAttenuation', 60, 'SampleRate', f_s, 'DesignMethod', 'butter', 'MatchExactly', 'passband');
% lpfilter = designfilt('lowpassiir', 'PassbandFrequency', f_c, 'StopbandFrequency', 10e3, 'PassbandRipple', 1, 'StopbandAttenuation', 60, 'SampleRate', f_s, 'DesignMethod', 'cheby1');
coeffs = lpfilter.Coefficients;

t = 0:0.000001:2;
ch = chirp(t,1,2,f_s,'logarithmic');

% ---- scale coefficients ---- 
scaled_coeffs = floor((coeffs ./ max(abs(coeffs), [], 2)) .* 2^(bit_width - 1));
% scaled_coeffs = floor((coeffs ./ max(max(abs(coeffs))) .* 2^bit_width));


% ---- proper way of using a filter ----
filt = filter(scaled_coeffs(1, 1 : 3), scaled_coeffs(1, 4 : 6), ch);

for i = 2:1:size(scaled_coeffs, 1) 
    filt = filter(scaled_coeffs(i, 1 : 3), scaled_coeffs(i, 4 : 6), filt);  
end
% figure; 
% plot(t, filt);
% title('proper way')
% f = fvtool(scaled_coeffs);
% f.Fs = f_s;
% 
% window_resize;


% ---- own implementation of the formula ----
% y[n] = 1 / a_0 * (b_0 * x[n] + b_1 * x[n - 1] + b_2 * x[n - 2]
%        - a_1 * y[n - 1] - a_2 * y[n - 2]
if do_scale_stuff == 1
    x = ch;
    y = x;
    co = scaled_coeffs;
    b0 = 1;
    b1 = 2;
    b2 = 3;
    a0 = 4; 
    a1 = 5;
    a2 = 6;

    for i = 1:size(co, 1)
        for n=1:size(x, 2)
            if n < 3
                y(n) = 0;
            else
                y(n) = (co(i, b0) * x(n) + co(i, b1) * x(n-1) + co(i, b2) * x(n-2) - co(i, a1) * y(n-1) - co(i, a2) * y(n-2)) / co(i, a0);
            end
        end
    %     figure;
    %     plot(t, y);
        x = y;
    end
    figure;
    plot(t, y);
    title('my way')
end
% ---- test with existing pdm file ----
% y[n] = 1 / a_0 * (b_0 * x[n] + b_1 * x[n - 1] + b_2 * x[n - 2]
%        - a_1 * y[n - 1] - a_2 * y[n - 2]
if do_pdm_stuff == 1
    pdm_data = fopen('silence.bmp', 'r');
    pdm = zeros(1, 4000);
    pdm(1, :) = fread(pdm_data, 4000, '*ubit1', 'ieee-be');

    for i=size(pdm, 2)
        if pdm(1, i) == 1
            pdm(1, i) = 255;
        else
            pdm(1, i) = -255;
        end
    end

    x = pdm;
    y = x;
    co_pdm = scaled_coeffs;
    b0 = 1;
    b1 = 2;
    b2 = 3;
    a0 = 4; 
    a1 = 5;
    a2 = 6;

    for i = 1:size(co_pdm, 1)
        for n=1:size(x, 2)
            if n < 3
                y(n) = 0;
            else
                y(n) = (co_pdm(i, b0) * x(n) + co_pdm(i, b1) * x(n-1) + co_pdm(i, b2) * x(n-2) - co_pdm(i, a1) * y(n-1) - co_pdm(i, a2) * y(n-2)) / co_pdm(i, a0);
            end
        end
        x = y;
    end

    % --- decimation ----
    steps = 192;
    counter = 1;
    y_dec = zeros(1, floor(size(y,2)/192));
    y_cnt = 1;
    for i = 1:size(y, 2)
        if counter == 1
            y_dec(y_cnt) = y(i);
            y_cnt = y_cnt + 1;
        elseif counter == 192
            counter = 0;
        end
        counter = counter + 1;
    end
    % figure;
    % plot(1:4000, pdm);
    % title('pdm data')
    % figure;
    % f_pdm = plot(1:4000, floor(y));
    % title('pdm data')
    fclose(pdm_data);

    figure
    plot(1:size(y_dec, 2), floor(y_dec))
    title('decimated signal')
end

% ---- mission: get rid of a0 ----
if do_get_rid == 1
    mis_coeffs = coeffs;
    % since a0 is just 1, we just ignore it
    %rid_coeffs = [mis_coeffs(:, 1:3), mis_coeffs(:, 5:6)];
    rid_coeffs = mis_coeffs;
    
    b0 = 1;
    b1 = 2;
    b2 = 3;
    a0 = 4; 
    a1 = 5;
    a2 = 6;
    % use filter 
    x = ch;
    y = x;
    for i = 1:size(rid_coeffs, 1)
        for n=1:size(x, 2)
            if n < 3
                y(n) = 0;
            else
                y(n) = (rid_coeffs(i, b0) * x(n) + rid_coeffs(i, b1) * x(n-1) + rid_coeffs(i, b2) * x(n-2) - rid_coeffs(i, a1) * y(n-1) - rid_coeffs(i, a2) * y(n-2)) / rid_coeffs(i, a0);
            end
        end
        x = y;
    end

    figure; 
    plot(t, x);
    title('got rid of a0')
    % scale that shit

    rid_scale_co = floor(rid_coeffs * 2^23);

    % use that scaled shit
    x = ch;
    y = x;
    for i = 1:size(rid_scale_co, 1)
        for n=1:size(x, 2)
            if n < 3
                y(n) = 0;
            else
                y(n) = (rid_scale_co(i, b0) * x(n) + rid_scale_co(i, b1) * x(n-1) + rid_scale_co(i, b2) * x(n-2) - rid_scale_co(i, a1) * y(n-1) - rid_scale_co(i, a2) * y(n-2)) / rid_scale_co(i, a0);
            end
        end
        x = y;
    end


    figure; 
    plot(t, y);
    title('scaled that shit')
end

% ---- test with existing pdm file ----
% y[n] = 1 / a_0 * (b_0 * x[n] + b_1 * x[n - 1] + b_2 * x[n - 2]
%        - a_1 * y[n - 1] - a_2 * y[n - 2]
if do_rid_pdm_stuff == 1
    pdm_data = fopen('silence.bmp', 'r');
    pdm = zeros(1, 4000);
    pdm(1, :) = fread(pdm_data, 4000, '*ubit1', 'ieee-be');
    
    scaled_pdm = zeros(size(pdm));
    pdm = pdm .* 2^32;
    pdm = pdm - 2^31;
    
    x = pdm;
    y = x;
    co_pdm = rid_scale_co;
    b0 = 1;
    b1 = 2;
    b2 = 3;
    a0 = 4; 
    a1 = 5;
    a2 = 6;

    for i = 1:size(co_pdm, 1)
        for n=1:size(x, 2)
            if n < 3
                y(n) = 0;
            else
                y(n) = (co_pdm(i, b0) * x(n) + co_pdm(i, b1) * x(n-1) + co_pdm(i, b2) * x(n-2) - co_pdm(i, a1) * y(n-1) - co_pdm(i, a2) * y(n-2)) / co_pdm(i, a0);
            end
        end
        x = y;
    end

    % --- decimation ----
    steps = 192;
    counter = 1;
    y_dec = zeros(1, floor(size(y,2)/192));
    y_cnt = 1;
    for i = 1:size(y, 2)
        if counter == 1
            y_dec(y_cnt) = y(i);
            y_cnt = y_cnt + 1;
        elseif counter == 192
            counter = 0;
        end
        counter = counter + 1;
    end
    fclose(pdm_data); 
    figure
    plot(1:size(y_dec, 2), floor(y_dec))
    title('decimated rid signal')
end

