
t = linspace(-5,5,1000);
x = 0;
K = 50;
w = 2*pi/2;
for k = -K:K
    % fourier series coefficient
    if k ~=0
        fsc = -exp(1j*pi*k)/(1j*pi*k);
    else
        fsc = 0;
    end
    % synthesis running sum
    x = x + fsc*exp(1j*w*t*k);
end

plot(t,x)