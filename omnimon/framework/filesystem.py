import os
import sys

from pyface.api import ImageResource

# Major package imports.
from fs.errors import FSError
from fs.opener import Opener, OpenerRegistry, _FSClosingFile, opener, fsopen
import wx

import logging
log = logging.getLogger(__name__)

from omnimon import __version__, __author__, __author_email__, __url__
substitutes = {
    'prog': 'Omnimon Editor',
    'yearrange': '2014-2015',
    'version': __version__,
    'description': "The Atari 8-bit binary editor & disassembler",
    'author': __author__,
    'author_email': __author_email__,
    'url': __url__,
    'license': "Application licensed under the GPLv3; most code also dual licensed under GPLv2",
    'warning': """<P>This code is still under development, so make backups and save often.""",
    'license_text': """This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
""",
    'authors': "",
    'contributors': """<p>Contributors to Omnimon:</p>
<ul>
<li>Mark James for the <a href=\"http://www.famfamfam.com/lab/icons/silk/\">free silk icon set</a>
<li>Chris Barker for bug reports and fixes on OS X</a>
<li>Kevin Savetz of <a href=\"http://ataripodcast.com\">ANTIC, the Atari Podcast</a> for beta testing
<li>David Beazley, author of <a href="\http://dabeaz.com\">Python Cookbook, 3rd Ed. and more</a>, for the 6502 mini assembler
</ul>""",
    }
substitutes['copyright'] = 'Copyright (c) %(yearrange)s %(author)s (%(author_email)s)' % substitutes

about = {
    "omnimon": """<html>
<h2>%(prog)s %(version)s</h2>

<p><img src="about://logo.png">

<h3>%(description)s</h3>

<p>%(copyright)s</p>

<p>%(license)s</p>

<p>%(warning)s</p>

<p>%(contributors)s</p>
""" % substitutes,
    "logo.png": ImageResource('omnimon256'),
    }


# FIXME: can't seem to figure out how to create a subclass of InputStream,
# so can't create a new FSFile object directly from the file in the fs
# about: filesystem.  So, fake the about: filesystem for the HTML control
# by duplicating the file from the fs about: filesystem and passing that
# wx.FSFile object

#class MemoryInputStream(wx.InputStream):
#    def __init__(self, fh):
#        wx.InputStream.__init__(self)
#        self.fh = fh
#        self.cursor = 0
#        
#    def OnSysRead(self, *args):
#        log.error("OnSysRead!!!!!")

class WxAboutFileSystemHandler(wx.FileSystemHandler):
    def CanOpen(self, location):
        return self.GetProtocol(location) == "about"
    
    def OpenFile(self, fs, location):
        # For some reason, the actual path shows up as the right location
        # rather than left, and it includes the leading slashes.
        path = self.GetRightLocation(location).lstrip("/")
        wxfs = wx.FileSystem()
        fsfile = wxfs.OpenFile("memory:%s" % path)
        if fsfile is None:
            try:
                fh = opener.open(location, "rb")
            except FSError, e:
                print str(e)
                return None
            log.debug("Created %s in wxMemoryFS" % path)
            wx.MemoryFSHandler.AddFile(path, fh.read())
            
            fsfile = wxfs.OpenFile("memory:%s" % path)
        else:
            log.debug("Found %s in wxMemoryFS" % path)
        return fsfile


def parse_with_about(self, fs_url, default_fs_name=None, writeable=False, create_dir=False, cache_hint=True):
    """Handle special "about://" URLs.  Normal parse function puts the path
    part of the about: url into the url2 component, not the path. E.g.
    
    >>> opener.split_segments("about://omnimon").groups()
    ('about', None, None, 'omnimon', None)
    
    Adding a bang character puts the subsequent chars in the path component:
    
    >>> opener.split_segments("about://omnimon!oeuae").groups()
    ('about', None, None, 'omnimon', 'oeuae')
    
    so putting the bang character immediately after the protocol causes the
    path to appear in the right place:
    
    >>> opener.split_segments("about://!omnimon!oeuae").groups()
    ('about', None, None, '', 'omnimon!oeuae')
    
    """
    match = self.split_segments(fs_url)
    if match:
        fs_name, credentials, url1, url2, path = match.groups()
        if fs_name == "about":
            # Force the path
            fs_url = "about://!%s" % url2
    return self.old_parse(fs_url, default_fs_name, writeable, create_dir, cache_hint)

OpenerRegistry.old_parse = OpenerRegistry.parse
OpenerRegistry.parse = parse_with_about

class AboutOpener(Opener):
    names = ['about']
    desc = """In-memory filesystem that holds files until the exiting the application

examples:
* about:// (opens a new memory filesystem)
* about://foo/bar (opens a new memory filesystem with subdirectory /foo/bar)
    """
    
    about_fs = None

    @classmethod
    def get_fs(cls, registry, fs_name, fs_name_params, fs_path,  writeable, create_dir):
        if cls.about_fs is None:
            from fs.memoryfs import MemoryFS
            cls.about_fs = MemoryFS()
        memfs = cls.about_fs
        if create_dir:
            memfs = memfs.makeopendir(fs_path)
        return memfs, None

def init_filesystems():
    wx.FileSystem.AddHandler(WxAboutFileSystemHandler())
    wx.FileSystem.AddHandler(wx.MemoryFSHandler())

    init_about_filesystem()
#    
#    for name in about.iterkeys():
#        url = "about://%s" % name
#        fh = opener.open(url, "rb")
#        text = fh.read()
#        print "Found %s, length=%d" % (name, len(text))
#        match = opener.split_segments(url)
#        stuff = match.groups()
#        print "url=%s, stuff=%s" % (url, str(stuff))
#        fs, path = opener.parse(url)
#        print "fs=%s (%s), path=%s" % (fs, id(fs), path)

def init_about_filesystem():
    opener.add(AboutOpener)
    for name, text in about.iteritems():
        url = "about://%s" % name
        fh = opener.open(url, "wb")
        if hasattr(text, 'create_bitmap'):
            fhb = opener.open(text.absolute_path, "rb")
            text = fhb.read()
            fhb.close()
        fh.write(text)
        fh.close()
        log.debug("Created %s" % url)