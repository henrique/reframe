# Copyright 2016-2020 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os

import reframe as rfm
import reframe.utility.os_ext as os_ext
import reframe.utility.sanity as sn


@rfm.required_version('>=2.14')
@rfm.parameterized_test(*([lang, linkage] for lang in ['cpp', 'c', 'f90']
                          for linkage in ['dynamic', 'static']))
class NetCDFTest(rfm.RegressionTest):
    def __init__(self, lang, linkage):
        lang_names = {
            'c': 'C',
            'cpp': 'C++',
            'f90': 'Fortran 90'
        }
        self.lang = lang
        self.linkage = linkage
        self.descr = lang_names[lang] + ' NetCDF ' + linkage.capitalize()
        self.valid_systems = ['daint:gpu', 'daint:mc',
                              'dom:gpu', 'dom:mc', 'kesch:cn', 'tiger:gpu',
                              'arolla:cn', 'tsa:cn']
        if self.current_system.name in ['daint', 'dom', 'tiger']:
            self.valid_prog_environs = ['PrgEnv-cray', 'PrgEnv-gnu',
                                        'PrgEnv-intel', 'PrgEnv-pgi']
            self.modules = ['cray-netcdf']
        elif self.current_system.name == 'kesch':
            self.exclusive_access = True
            if linkage == 'dynamic':
                self.valid_prog_environs = ['PrgEnv-pgi-nompi']

            if lang != 'f90':
                self.valid_prog_environs += ['PrgEnv-cray-nompi']
        elif self.current_system.name in ['arolla', 'tsa']:
            self.exclusive_access = True
            self.valid_prog_environs = ['PrgEnv-gnu-nompi', 'PrgEnv-pgi-nompi']

        self.sourcesdir = os.path.join(self.current_system.resourcesdir,
                                       'netcdf')
        self.build_system = 'SingleSource'
        self.sourcepath = 'netcdf_read_write.' + lang
        self.num_tasks = 1
        self.num_tasks_per_node = 1
        self.sanity_patterns = sn.assert_found(r'SUCCESS', self.stdout)
        self.maintainers = ['AJ', 'SO']
        self.tags = {'production', 'craype', 'external-resources'}

    @rfm.run_before('compile')
    def setflags(self):
        if self.current_system.name == 'kesch':
            if self.current_environ.name == 'PrgEnv-cray-nompi':
                self.modules = ['netcdf/4.4.1.1-gmvolf-17.02',
                                'netcdf-c++/4.3.0-gmvolf-17.02',
                                'netcdf-fortran/4.4.4-gmvolf-17.02']
                self.build_system.cppflags = [
                    '-I$EBROOTNETCDF/include',
                    '-I$EBROOTNETCDFMINCPLUSPLUS/include',
                    '-I$EBROOTNETCDFMINFORTRAN/include'
                ]
                self.build_system.ldflags = [
                    '-L$EBROOTNETCDF/lib',
                    '-L$EBROOTNETCDFMINCPLUSPLUS/lib',
                    '-L$EBROOTNETCDFMINFORTRAN/lib',
                    '-L$EBROOTNETCDF/lib64',
                    '-L$EBROOTNETCDFMINCPLUSPLUS/lib64',
                    '-L$EBROOTNETCDFMINFORTRAN/lib64',
                    '-lnetcdf', '-lnetcdf_c++4', '-lnetcdff'
                ]
            elif self.current_environ.name == 'PrgEnv-pgi-nompi':
                self.modules = ['netcdf/4.6.1-pgi-18.5-gcc-5.4.0-2.26',
                                'netcdf-c++/4.3.0-pgi-18.5-gcc-5.4.0-2.26',
                                'netcdf-fortran/4.4.4-pgi-18.5-gcc-5.4.0-2.26']
                self.build_system.ldflags = [
                    '-B' + self.linkage,
                    '-L$EBROOTNETCDF/lib',
                    '-L$EBROOTNETCDFMINCPLUSPLUS/lib',
                    '-L$EBROOTNETCDFMINFORTRAN/lib',
                    '-L$EBROOTNETCDF/lib64',
                    '-L$EBROOTNETCDFMINCPLUSPLUS/lib64',
                    '-L$EBROOTNETCDFMINFORTRAN/lib64',
                    '-lnetcdf', '-lnetcdf_c++4', '-lnetcdff'
                ]
                self.build_system.fflags = [
                    '-I$EBROOTNETCDF/include',
                    '-I$EBROOTNETCDFMINCPLUSPLUS/include',
                    '-I$EBROOTNETCDFMINFORTRAN/include'
                ]
        elif self.current_system.name in ['arolla', 'tsa']:
            self.modules = ['netcdf', 'netcdf-c++', 'netcdf-fortran']
            self.build_system.cppflags = [
                '-I$EBROOTNETCDF/include',
                '-I$EBROOTNETCDFMINCPLUSPLUS/include',
                '-I$EBROOTNETCDFMINFORTRAN/include'
            ]
            self.build_system.ldflags = [
                '-L$EBROOTNETCDF/lib',
                '-L$EBROOTNETCDFMINCPLUSPLUS/lib',
                '-L$EBROOTNETCDFMINFORTRAN/lib',
                '-L$EBROOTNETCDF/lib64',
                '-L$EBROOTNETCDFMINCPLUSPLUS/lib64',
                '-L$EBROOTNETCDFMINFORTRAN/lib64',
                '-lnetcdf', '-lnetcdf_c++4', '-lnetcdff'
            ]
        else:
            self.build_system.ldflags = ['-%s' % self.linkage]

    @rfm.run_before('compile')
    def cray_linker_workaround(self):
        # NOTE: Workaround for using CCE < 9.1 in CLE7.UP01.PS03 and above
        # See Patch Set README.txt for more details.
        cle = os_ext.cray_cle_info()
        if not cle:
            return

        if (cle.release == '7.0.UP01' and cle.patchset >= '03'):
            self.variables['LINKER_X86_64'] = '/usr/bin/ld'

    @rfm.run_before('run')
    def cdt2006_cpp_workaround(self):
        if (os_ext.cray_cdt_version() == '20.06' and self.lang == 'cpp'):
            self.modules += ['cray-hdf5/1.10.6.1']
