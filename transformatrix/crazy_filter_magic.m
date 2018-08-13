close all;
f_s = 3072000;
f_c = 8e3;
bit_width = 32;
lpfilter = designfilt('lowpassiir', 'PassbandFrequency', f_c, 'StopbandFrequency', 15e3, 'PassbandRipple', 1, 'StopbandAttenuation', 60, 'SampleRate', f_s, 'DesignMethod', 'butter', 'MatchExactly', 'passband');
% lpfilter = designfilt('lowpassiir', 'PassbandFrequency', f_c, 'StopbandFrequency', 10e3, 'PassbandRipple', 1, 'StopbandAttenuation', 60, 'SampleRate', f_s, 'DesignMethod', 'cheby1');
coeffs = lpfilter.Coefficients;

t = 0:0.000001:2;
ch = chirp(t,1,2,f_s,'logarithmic');

scaled_coeffs = floor((coeffs ./ max(abs(coeffs), [], 2)) .* 2^(bit_width - 1));
% scaled_coeffs = floor((coeffs ./ max(max(abs(coeffs))) .* 2^bit_width));


% ---- proper way of using a filter ----
filt = filter(scaled_coeffs(1, 1 : 3), scaled_coeffs(1, 4 : 6), ch);

for i = 2:1:size(scaled_coeffs, 1) 
    filt = filter(scaled_coeffs(i, 1 : 3), scaled_coeffs(i, 4 : 6), filt);  
end
figure; 
plot(t, filt);
title('proper way')
f = fvtool(scaled_coeffs);
f.Fs = f_s;

window_resize;


% ---- own implementation of the formula ----
% y[n] = 1 / a_0 * (b_0 * x[n] + b_1 * x[n - 1] + b_2 * x[n - 2]
%        - a_1 * y[n - 1] - a_2 * y[n - 2]
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

% ---- test with existing pdm file ----
% y[n] = 1 / a_0 * (b_0 * x[n] + b_1 * x[n - 1] + b_2 * x[n - 2]
%        - a_1 * y[n - 1] - a_2 * y[n - 2]
pdm_data = fopen('silence.bmp', 'r');
pdm = zeros(1, 4000);
pdm(1, :) = fread(pdm_data, 4000, '*ubit1', 'ieee-be');

pdm = pdm .* 255;

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
%     figure;
%     plot(t, y);
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
figure;
plot(1:4000, pdm);
title('pdm data')
figure;
f_pdm = plot(1:4000, floor(y));
title('pdm data')
fclose(pdm_data);

figure
plot(1:size(y_dec, 2), floor(y_dec))
title('decimated signal')