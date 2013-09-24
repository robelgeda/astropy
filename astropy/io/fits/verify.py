# Licensed under a 3-clause BSD style license - see PYFITS.rst

import warnings

from .util import indent, u
from ...utils.custom_warnings import AstropyUserWarning


class VerifyError(Exception):
    """
    Verify exception class.
    """
    pass


class VerifyWarning(AstropyUserWarning):
    """
    Verify warning class.
    """


class _Verify(object):
    """
    Shared methods for verification.
    """

    def run_option(self, option='warn', err_text='', fix_text='Fixed.',
                   fix=None, fixable=True):
        """
        Execute the verification with selected option.
        """

        text = err_text

        if not fixable:
            option = 'unfixable'

        if option in ['warn', 'exception']:
            pass
        # fix the value
        elif option == 'unfixable':
            text = 'Unfixable error: %s' % text
        else:
            if fix:
                fix()
            text += '  ' + fix_text
        return text

    def verify(self, option='warn'):
        """
        Verify all values in the instance.

        Parameters
        ----------
        option : str
            Output verification option.  Must be one of ``"fix"``,
            ``"silentfix"``, ``"ignore"``, ``"warn"``, or
            ``"exception"``.  See :ref:`verify` for more info.
        """

        opt = option.lower()
        if opt not in ['fix', 'silentfix', 'ignore', 'warn', 'exception']:
            raise ValueError('Option %s not recognized.' % option)

        if opt == 'ignore':
            return

        x = str(self._verify(opt)).rstrip()
        if opt in ['fix', 'silentfix'] and 'Unfixable' in x:
            raise VerifyError('\n' + x)
        if opt not in ['silentfix', 'exception'] and x:
            warnings.warn(u('Output verification result:'), VerifyWarning)
            for line in x.splitlines():
                # Each line contains a single issue that was fixed--issue a
                # separate warning for each of those issues
                warnings.warn(line, VerifyWarning)
            warnings.warn(u('Note: Astropy uses zero-based indexing.\n'), VerifyWarning)
        if opt == 'exception' and x:
            raise VerifyError('\n' + x)


class _ErrList(list):
    """
    Verification errors list class.  It has a nested list structure
    constructed by error messages generated by verifications at
    different class levels.
    """

    def __init__(self, val, unit='Element'):
        list.__init__(self, val)
        self.unit = unit

    def __str__(self):
        return self._display()

    def _display(self, ind=0):
        """
        Print out nested structure with corresponding indentations.
        """

        result = []
        element = 0

        # go through the list twice, first time print out all top level
        # messages
        for item in self:
            if not isinstance(item, _ErrList):
                result.append('%s\n' % indent(item, shift=ind))

        # second time go through the next level items, each of the next level
        # must present, even it has nothing.
        for item in self:
            if isinstance(item, _ErrList):
                tmp = item._display(ind=ind + 1)

                # print out a message only if there is something
                if tmp.strip():
                    if self.unit:
                        result.append(indent('%s %s:\n' % (self.unit, element),
                                      shift=ind))
                    result.append(tmp)
                element += 1

        return ''.join(result)
