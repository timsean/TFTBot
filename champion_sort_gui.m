% TFT champion model sorting gui
% Kevin Joe
% Last Edit: April 4, 2020

% It reads through all images in the "unlabeled" folder and moves the image
% file into the corresponding folder based on user response. 


% Instructions: 
% 1) Press run or type champion_sort_gui in command window
% 2) Given the unlabeled image, click the corresponding champion or empty
% 3) If you made a mistake, you can click the undo button, but it only goes
%    back one step, and nothing more.




function champion_sort_gui()

MyFigure = figure('units','normalized','outerposition',[0.2 0.2 0.8 0.8]);

dir_str = 'champion_model/unlabeled/';

directory = dir(dir_str);
c = 3;
subplot(1,2,1)

curr_file = [dir_str,directory(c).name];
dest_file = [dir_str,directory(c).name];
imshow(curr_file)


completed = uicontrol('Style','Text','String', 'Completed: 0' ,...
            'units','normalized','position', [0.1 0.95 0.1 0.05],...
            'Fontsize',15);

remain_str = sprintf('Total: %d', length(directory));
remaining = uicontrol('Style','Text','String', remain_str  ,...
    'units','normalized','position', [0.2 0.95 0.1 0.05],...
    'Fontsize',15);

x = [0.55, 0.68, 0.81];
y = linspace(0,1,19);
y = flip(y(2:end-1));

t = readtable('champlist.csv','ReadVariableNames',0);
k = 1;
for i = 1:3
    for j = 1:17
        uicontrol('Style','Pushbutton','String',t.Var1{k},'Callback',@select, ...
        'units','normalized','position', [x(i), y(j), 0.1 0.04],...
        'fontsize', 20);
    
        k=k+1;
    end
end

uicontrol('Style','Pushbutton','String','Empty','Callback',@select, ...
'units','normalized','position', [0.1,0.02, 0.1 0.05],...
'fontsize', 20);

uicontrol('Style','Pushbutton','String','Delete','Callback',@select, ...
'units','normalized','position', [0.225,0.02, 0.1 0.05],...
'fontsize', 20);

uicontrol('Style','Pushbutton','String','Undo','Callback',@undo, ...
'units','normalized','position', [0.35,0.02, 0.1 0.05],...
'fontsize', 20);

% display_text = uicontrol('Style','Text','String','');

    function select(whichbutton,~) 
        select_champ = whichbutton.String;
        disp(select_champ)
        
        dest_loc = ['champion_model/',select_champ, '/'];
        L = length(dir(dest_loc)) + 1;
        
        dest_file = [dest_loc, num2str(L), '.png'];
        
        disp(curr_file)
        disp(dest_file)
        movefile(curr_file,dest_file)
        
        try
            c = c+1;
            curr_file = [dir_str ,directory(c).name];
            subplot(1,2,1)
            imshow(curr_file)
            
            completed.String = sprintf('Completed: %d', c-3);
            
        catch
            delete(MyFigure)
        end

    end
    
    function undo(~,~) 
        if c > 3
            c = c-1;
            curr_file = [dir_str ,directory(c).name];
            
            disp(dest_file)
            disp(curr_file)
            movefile(dest_file,curr_file)
            
            subplot(1,2,1)
            imshow(curr_file)
            
        end
    end

end