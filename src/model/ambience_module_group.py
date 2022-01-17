# ambience_module_group.py
#
# Copyright 2022 Luka Jankovic
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class AmbienceModuleGroupException(Exception):
    """
    Raised when a function call is made directly onto an AmbienceModuleGroup 
    object.
    """

class AmbienceModuleGroup():
    """
    Template class for connecting a group to Ambience.
    """

    def __init__(self, devices):
        raise AmbienceModuleGroupException
    
    def set_color(self, hsvk):
        raise AmbienceModuleGroupException

    def set_infrared(self, infrared):
        raise AmbienceModuleGroupException

    def set_power(self, power):
        raise AmbienceModuleGroupException