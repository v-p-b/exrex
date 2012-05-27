#!/usr/bin/env python

# This file is part of exrex.
#
# exrex is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# exrex is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with exrex. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2012- by Adam Tauber, <asciimoo@gmail.com>

from re import sre_parse
from itertools import product, repeat

CATEGORIES = {'category_space'  : sre_parse.WHITESPACE
             ,'category_digit'  : sre_parse.DIGITS
             ,'category_any'    : [chr(x) for x in range(32, 123)]
             }

def _p(d, append=False):
    """docstring for _p"""
    #print d
    ret =[]
    ranges = ['']
    if not isinstance(d, list):
        print '[!] not a list: %r' % d
        return []
    if not len(d):
        print '[!] empty list'
        return []
    l = ''
    for i in d:
        if len(ranges) and i[0] != 'range':
            if len(ret):
                tmp_ret = []
                for char in ranges:
                    for k,_ in enumerate(ret):
                        tmp_ret.append(ret[k]+char)
                ret = tmp_ret
            else:
                ret = ranges
            ranges = []

        if i[0] == 'literal':
            if append:
                if ret[0] == '':
                    ret[0] = chr(i[1])
                else:
                    ret.append(chr(i[1]))
            else:
                for k,_ in enumerate(ret):
                    ret[k] += chr(i[1])
        elif i[0] == 'subpattern':
            for sub in i[1:]:
                tmp_ret = []
                for piece in _p(list(sub[1])):
                    for k,_ in enumerate(ret):
                        tmp_ret.append(ret[k]+piece)
                if len(tmp_ret):
                    ret = tmp_ret
        elif i[0] == 'in':
            tmp_ret = []
            for piece in _p(list(i[1]), True):
                for k,_ in enumerate(ret):
                    tmp_ret.append(ret[k]+piece)
            ret = tmp_ret
        elif i[0] == 'range':
            ranges.extend(map(chr, range(i[1][0], i[1][1]+1)))
        elif i[0] == 'max_repeat':
            tmp_ret = []
            chars = [x for x in _p(list(i[1][2])) if x != '']
            ret = [r+''.join(piece) for rep in range(i[1][0], i[1][1]+1) for piece in product(*repeat(chars, rep)) for r in ret]
            # tmp_ret = []
            # for piece in _p(list(i[1][2])):
            #     for rep in range(i[1][0], i[1][1]+1):
            #         for r in ret:
            #             tmp_ret.append(r+piece*rep)
            # ret = tmp_ret
        elif i[0] == 'category':
            cat = CATEGORIES.get(i[1], [''])
            ret = [r+c for r in ret for c in cat]
        elif i[0] == 'branch':
            subs = []
            for piece in [_p(list(x)) for x in i[1][1]]:
                subs.extend(piece)
            ret = [r+s for r in ret for s in subs]
        elif i[0] == 'any':
            ret = [r+c for c in CATEGORIES['category_any'] for r in ret]

    if len(ranges):
        if len(ret) and ret[0] != '':
            tmp_ret = []
            for char in ranges:
                for k,_ in enumerate(ret):
                    tmp_ret.append(ret[k]+char)
            ret = tmp_ret
        else:
            ret = ranges
    #print ret
    return ret


def parse(s):
    """docstring for parse"""
    r = sre_parse.parse(s)
    # print r
    return _p(list(r))


def argparser():
    import argparse
    from sys import stdout
    argp = argparse.ArgumentParser(description='exrex - regular expression string generator')
    argp.add_argument('-o', '--output'
                     ,help      = 'Output file - default is STDOUT'
                     ,metavar   = 'FILE'
                     ,default   = stdout
                     ,type      = argparse.FileType('w')
                     )
    argp.add_argument('-d', '--delimiter'
                     ,help      = 'Delimiter - default is \\n'
                     ,default   = '\n'
                     )
    argp.add_argument('-v', '--verbose'
                     ,action    = 'count'
                     ,help      = 'Verbosity level - default is 3'
                     ,default   = 3
                     )
    argp.add_argument('regex'
                     ,metavar   = 'REGEX'
                     ,help      = 'REGEX string'
                     )
    return vars(argp.parse_args())

def __main__():
    # 'as(d|f)qw(e|r|s)[a-zA-Z]{2,3}'
    # 'as(QWE|Z([XC]|Y|U)V){2,3}asdf'
    # '.?'
    args = argparser()
    for s in parse(args['regex']):
        args['output'].write(s+args['delimiter'])

if __name__ == '__main__':
    __main__()