clear all
%----------------------------- Choices  -----------------------------%
IDF           = [0    0   1];
processSuffix = {'.np','','' };
suffOut       = {'.np', '.BL', '.IDF'}; 
%----------------------------- Setup  -----------------------------%
datadir  = 'output'
outDir = 'output'

%Get things pulled in, sorted and named. 
for p = 1:length(processSuffix)
    % Read in the data 
    rawtdm = dlmread([ datadir 'tdm.sparse' processSuffix{p} '.csv'], ',');
    M      = sparse(rawtdm(:,2)+1, rawtdm(:,1)+1, rawtdm(:,3));
    docs   = textread([datadir 'tdm.docs' processSuffix{p} '.csv'], '%s');
    words  = textread([datadir 'tdm.words' processSuffix{p} '.csv'], '%s');
    %Sort everything
    [docs, Idocs] = sort(docs);
    [words, Iwords] = sort(words);    
    M = full(M(Iwords, Idocs));
    %Name things properly
    eval(['M'     int2str(p) ' = M;']);
    eval(['docs'  int2str(p) ' = docs;']);
    eval(['words' int2str(p) ' = words;']);    
    clearvars M rawtdm docs words Idocs Iwords; 
end

%----------------------------- Preprocessing  -----------------------------%
for p = 1:length(processSuffix)
    eval(['M = M' int2str(p) ';']);    
    if IDF(p)
          n = size(M,2);
          binary = M > 0;
          n_i = sum(binary,2);
          IDFvec = log((ones(size(M,1),1)./n_i)*n);
          IDFmat = repmat(IDFvec, 1, size(M,2));
          M = M.*IDFmat;
          eval(['IDFvec' int2str(p) '= IDFvec;']);
      end
    
    eval(['M'     int2str(p) ' = M;']);
    clearvars M;
end
       
%----------------------------- Persistence  -----------------------------%       
dates = char(docs1);
datesNum = str2num(dates(:,16:24));
%datesNum = datenum(dates, 'yyyymmdd');
PERSISTENCE = NaN(length(datesNum), length(suffOut)); 
titles = ''; 
for p = 1:length(processSuffix)
    eval(['M = M' int2str(p) ';']);    
    stChange = NaN(1,size(M,2))';
    for i = 2:size(M,2)
        stChange(i) = cossim(M(:,i), M(:,i-1));
    end
    PERSISTENCE(:,p) = stChange; 
    titles = [titles, ',', suffOut{p}]; 
end
f = fopen([outDir 'PERSISTENCE.csv'], 'w'); 
fprintf(f, [titles '\n']); 
fprintf(f, '%8.0f,%1.2f,%1.2f,%1.2f\n',[datesNum, PERSISTENCE ]');
[datesNum, PERSISTENCE ]
fclose(f)
    
