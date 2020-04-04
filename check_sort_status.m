% check status of sorting

t = readtable('champlist.csv','ReadVariableNames',0);


label = t.Var1;
distribution = zeros(54,1);
for k = 1:51
    str = t.Var1{k};
    
    d = dir(['champion_model/' , str]);
    distribution(k) = length(d) - 2;
end

d = dir('champion_model/Empty');
distribution(52) = length(d) - 2;
label{52} = 'Empty';

d = dir('champion_model/Delete');
distribution(53) = length(d) - 2;
label{53} = 'Delete';

d = dir('champion_model/unlabeled');
distribution(54) = length(d) - 2;
label{54} = 'unlabeled';

bar(distribution)
set(gca, 'XTick',1:54, 'XtickLabel',label)
xtickangle(45)