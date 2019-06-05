close all;

outputdir = 'C:/Users/jordi/code/muddy/data/rsk';
datadir = 'D:/EE-FoT-May2017Expt/Concertos/RawData/';
files = {
    '066010_20170704_0850.rsk',...
    '065761_20170702_1030.rsk',...
    '065762_20170630_1524.rsk',...
    '065760_20170702_1005.rsk',...
    '066011_20170703_1431.rsk',...
    '065818_20170701_0947.rsk',...
    '065819_20170701_0953.rsk',...
    '065821_20170703_1419.rsk',...
    '065820_20170704_0838.rsk',...
};

tstart = datenum(2017, 05, 11, 12, 0, 0);
tend = datenum(2017, 06, 09, 12, 0, 0);

for i = 1 : length(files)
    fprintf('%s\n', files{i});
    f = RSKopen([datadir files{i}]);
    rsk = RSKreaddata(f, 't1', tstart, 't2', tend);
    fprintf('File read - now processing measurements');
    % Correct for A2D zero-order hold
    rsk = RSKcorrecthold(rsk, 'action', 'interp');
    % Remove atmospheric pressure from measured total pressure
    % We suggest deriving sea pressure first, especially when an
    % atmospheric pressure other than the nominal value of 10.1325 dbar is
    % used, because deriving salinity and depth requires sea pressure.
    rsk = RSKderiveseapressure(rsk);
    rsk = RSKderivedepth(rsk);
    rsk = RSKderivesalinity(rsk);
    % save new RSK file
    nf = RSK2RSK(rsk, 'outputdir', outputdir, 'suffix', 'processed');
    fprintf('New processed file %s\n', nf);
    clear rsk;
    clear nf;
    clear f;
end

clear all;