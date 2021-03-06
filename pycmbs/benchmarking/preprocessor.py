# -*- coding: utf-8 -*-
"""
This file is part of pyCMBS. (c) 2012-2014
For COPYING and LICENSE details, please refer to the file
COPYRIGHT.md
"""

import os
import glob
import tempfile


class EnsemblePreprocessor(object):
    """
    class to perform preprocessing for model ensemble data.
    The purpose is in particular to preprocess ensemble members
    which are stored in different files and provide functionality for
    ensemble statistic calculations

    The processor basically provides a logic. Number crunching is
    exclusively done using the CDO's
    """

    def __init__(self, data_dir, outfile, **kwargs):
        """
        Parameters
        ----------
        data_dir : str
            root directory where the data is located
        outfile : str
            name of the output file to be generated. This then also
            automatically specifies the output directory, which
            will be generated in case it is not existing
        """
        self.output_dir, self.outfile = os.path.split(outfile)
        if len(self.output_dir) == 0:
            self.output_dir = './'
        self.data_dir = data_dir
        if self.data_dir[-1] != os.sep:
            self.data_dir += os.sep
        if self.output_dir[-1] != os.sep:
            self.output_dir += os.sep
        self.mergetime_files = []

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)


class CMIP5Preprocessor(EnsemblePreprocessor):
    """
    preprocessor for CMIP5 raw data
    it is assumed that data from the CMIP5 archive have been extracted
    already for a particular version and that the version directory
    has been removed from the overall path.
    """
    def __init__(self, data_dir, outfile, variable, model, experiment, **kwargs):
        """
        Parameters
        ----------

        data_dir : str
            root directory where the data is located; stored in the hierarcy like in the CMIP5 archive
        outfile : str
            name of output file
        variable : str
            cmor variable (e.g. 'pr' for precipitation)
        model : str
            name of model (e.g. MPI-ESM-LR)
        experiment : str
            experiment tag (e.g. 'amip')

        Within kwargs, the following parameters are mandatory
        mip : str
            specifies the MIP (e.g. 'Amon')
        realm : str
            specifies the domain (e.g. 'atmos')
        institute : str
            specifies the institute (e.g. MPI-M)
        """
        self.institute = kwargs.pop('institute', None)
        self.mip = kwargs.pop('mip', None)
        self.realm = kwargs.pop('realm', None)

        super(CMIP5Preprocessor, self).__init__(data_dir, outfile, **kwargs)
        self.variable = variable
        self.model = model
        self.experiment = experiment

        self._check()

    def _check(self):
        assert self.mip is not None, 'ERROR: a MIP needs to be provided'
        assert self.realm is not None, 'ERROR: a REALM needs to be provided'
        assert self.institute is not None, 'ERROR: a INSTITUTE needs to be provided'

    def _filelist(self, l):
        """
        generate a filelist as single string (e.g. for cdo usage
        """
        r = ''
        for x in l:
            r += x + ' '
        return r

    def _log(self, s):
        """ write string s to the logfile """
        logfile = self.output_dir + 'cmip5_preprocessor_' + self.experiment + '_' + self.variable + '.log'
        o = open(logfile, 'a')
        o.write(s + '\n')
        o.close()

    def mergetime(self, n, start_time=None, stop_time=None, delete=False):
        """
        perform mergetime for a single ensemble member
        In case that only a single file is used, generate only a link
        to the original data

        Parameters
        ----------
        n : int
            number of ensemble member
        start_time : datetime
            start time of period
        stop_time : datetime
            end time of period
        """
        if n not in self.ensemble_files.keys():
            print n
            raise ValueError('Ensemble not existing!')

        if start_time is not None:
            if stop_time is None:
                raise ValueError('Both, start_time and stop_time need to be specified!')
        if stop_time is not None:
            if start_time is None:
                raise ValueError('Both, start_time and stop_time need to be specified!')
        if start_time is not None:
            selstr = 'seldate,' + str(start_time)[0:10] + ',' + str(stop_time)[0:10]
        else:
            selstr = ''

        ens_files = self.ensemble_files[n]
        self._log(self.model + '\t' + str(n) + '\t' + str(len(ens_files)))  # model name, ensemble nr., files per ensemble member

        # create string with filenames
        fstr = self._filelist(ens_files)

        # output file
        ofile = self.output_dir + os.path.basename(ens_files[0]).split('r' + str(n) + 'i1p1')[0] + 'r' + str(n) + 'i1p1' + '_mergetime.nc'

        if start_time is not None:
            ofile += '_' + str(start_time)[0:10] + '_' + str(stop_time)[0:10]
        ofile += '.nc'

        self.mergetime_files.append(ofile)

        # cdo
        if selstr == '':
            cmd = 'cdo -f nc mergetime ' + fstr + ' ' + ofile
        else:
            # merge first and the select time (not the most performant way to do it)
            tmpfile = tempfile.mktemp(suffix='.nc')
            if os.path.exists(tmpfile):
                os.remove(tmpfile)
            cmd1 = 'cdo -f nc mergetime ' + fstr + ' ' + tmpfile
            os.system(cmd1)

            if not os.path.exists(tmpfile):
                tmp_s = 'Error in creating temporary file: ABORT! ' + self.model + ' ' + self.experiment + ' ' + tmpfile
                print tmp_s
                self._log(tmp_s)

            cmd = 'cdo -f nc ' + selstr + ' ' + tmpfile + ' ' + ofile

        # calculate final output file
        if os.path.exists(ofile):
            if delete:
                os.remove(ofile)
            else:
                self.mergetime_files.append(ofile)
                print('File already existing ... no processing is done')
                return

        print('Doing temporal preprocessing for ensemble member ... %s' % n)
        os.system(cmd)
        if os.path.exists(ofile):  # just ensure that everything wen well
            self.mergetime_files.append(ofile)


    def get_ensemble_files(self, maxens=50):
        """
        create a dictionary with filenames for the different ensemble
        members

        Parameters
        ----------
        maxens : int
            maximum ensemble member size
        """

        # create filelist for each ensemble
        res = {}
        cnt = 0
        for i in xrange(1, maxens + 1):
            w1 = self._get_file_wildcard(i)
            files = glob.glob(w1)
            cnt += len(files)
            if len(files) > 0:
                res.update({i: files})

        self.ensemble_files = res

    def _get_file_wildcard(self, ens):
        p = self.data_dir + self.institute + os.sep + self.model + os.sep + self.experiment + os.sep + 'mon' + os.sep + self.realm + os.sep + self.mip + os.sep + 'r' + str(ens) + 'i1p1' + os.sep + self.variable + os.sep + self.variable + '_' + self.mip + '_' + self.model + '_' + self.experiment + '_r' + '*.nc'
        return p

    def mergetime_ensembles(self, delete=False, start_time=None, stop_time=None):
        self.get_ensemble_files()
        for i in self.ensemble_files.keys():
            self.mergetime(i, delete=delete, start_time=start_time, stop_time=stop_time)

    def ensemble_mean(self, delete=False, start_time=None, stop_time=None):
        """
        Parameters
        ----------
        start_time : datetime
            start time of period
        stop_time : datetime
            end time of period
        """
        print('Doing ensemble mean calculation ...')
        # if temporal merged files are not yet there, do preprocessing
        if len(self.mergetime_files) < 2:
            self.mergetime_ensembles(delete=delete, start_time=start_time, stop_time=stop_time)

        if len(self.mergetime_files) < 2:
            print self.mergetime_files
            print 'No ensemble mean calculation possible as not enough files!'
            self._log('No ensemble mean calculation possible as not enough files! ' + self.institute + ' ' + self.model + ' ' + self.experiment)

        fstr = self._filelist(self.mergetime_files)

        # ensemble mean calculation
        ofile = self.output_dir + self.outfile
        ofile = os.path.splitext(ofile)[0]
        if start_time is not None:
            ofile += '_' + str(start_time)[0:10] + '_' + str(stop_time)[0:10]
        #~ ofile += '.nc'
        self.outfile = ofile
        self.outfile_ensmean = self.outfile + '_ensmean.nc'
        cmd = 'cdo -f nc ensmean ' + fstr + ' ' + self.outfile_ensmean
        if os.path.exists(ofile):
            if delete:
                os.remove(ofile)
                os.system(cmd)
            else:
                print('File already existing ... no processing is done')
        else:
            os.system(cmd)

        # ensemble standard deviation
        self.outfile_ensstd = self.outfile_ensmean.replace('_ensmean', '_ensstd')
        cmd = 'cdo -f nc ensstd ' + fstr + ' ' + self.outfile_ensstd
        if os.path.exists(self.outfile_ensstd):
            if delete:
                os.remove(self.outfile_ensstd)
                os.system(cmd)
            else:
                print('File already existing ... no processing is done')
        else:
            os.system(cmd)


class CMIP5ModelParser(object):
    """
    a parser to retrieve model and institute names
    """

    def __init__(self, root_dir):
        """
        Parameters
        ----------
        root_dir : str
            directory where the model data is located. A similar structure like
            in the CMIP5 archive of DKRZ is assumed (MiKlip server)
            Thus below the root directory needs to be first subdirectories
            of individual institutes.
        """
        self.root_dir = root_dir
        if self.root_dir[-1] != os.sep:
            self.root_dir += os.sep
        if not os.path.exists(self.root_dir):
            raise ValueError('Path not existing!')
        self.institutes = None
        self.models = None

    def get_institutes(self):
        """ get a list with all institutes """
        return [os.path.basename(f) for f in glob.glob(self.root_dir + '*')]

    def get_all_models(self):
        """ get a list with all models and institutes """
        r = {}
        for i in self.get_institutes():
            r.update({i: self._get_models4institute(i)})
        return r

    def _get_models4institute(self, institute):
        """ return a list of models from a particular institute """
        return [os.path.basename(f) for f in glob.glob(self.root_dir + institute + os.sep + '*')]

    def check_files_availablility(self, vars, institute, model, experiment):
        """
        check if files for the specified variables are existing
        in preprocessed form

        Parameters
        ----------
        vars : list
            list of variables to check e.g. ['rsds', 'rsus']; the

        Returns
        -------
        returns True if all files are existing, otherwise it returns False
        """
        raise ValueError('This functionality is not implemented yet!')
