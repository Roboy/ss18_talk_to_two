close all;
fs_sin =  3072000;                    % Sampling frequency (samples per second)
dt = 1/fs_sin;                   % seconds per sample
StopTime = (1/8) * 10^-3;             % seconds
t_sin = (0:dt:StopTime-dt)';     % seconds
F_8k = 8000;                      % Sine wave frequency (hertz)
F_1M = 1 * 10^6;
sin_8k = sin(2*pi*F_8k*t_sin);
sin_1M = sin(2*pi*F_1M*t_sin);
sin_comb = sin_8k + sin_1M;

figure; 
plot(t_sin, sin_8k);
title('8kHz sinus');

figure; 
plot(t_sin, sin_1M);
title('1MHz sinus');



figure; 
plot(t_sin, sin_comb);
title('combined sinus');
