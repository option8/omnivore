import sys

# Enthought library imports.
from envisage.ui.tasks.api import TasksApplication
from pyface.tasks.api import TaskWindowLayout
from traits.api import Bool, Instance, List, Property

# Local imports.
from peppy2.framework.preferences import FrameworkPreferences, \
    FrameworkPreferencesPane


class FrameworkApplication(TasksApplication):
    """ The sample framework Tasks application.
    """

    #### 'IApplication' interface #############################################

    # The application's globally unique identifier.
    id = 'peppy2.framework.application'

    # The application's user-visible name.
    name = 'Peppy2'

    #### 'TasksApplication' interface #########################################

    # The default window-level layout for the application.
    default_layout = List(TaskWindowLayout)

    # Whether to restore the previous application-level layout when the
    # applicaton is started.
    always_use_default_layout = Property(Bool)

    #### 'FrameworkApplication' interface ####################################

    preferences_helper = Instance(FrameworkPreferences)

    ###########################################################################
    # Private interface.
    ###########################################################################

    #### Trait initializers ###################################################

    def _default_layout_default(self):
        active_task = self.preferences_helper.default_task
        tasks = [ factory.id for factory in self.task_factories ]
        return [ TaskWindowLayout(*tasks,
                                  active_task = active_task,
                                  size = (800, 600)) ]

    def _preferences_helper_default(self):
        return FrameworkPreferences(preferences = self.preferences)

    #### Trait property getter/setters ########################################

    def _get_always_use_default_layout(self):
        return self.preferences_helper.always_use_default_layout


    #### Trait event handlers
    
    def _application_initialized_fired(self):
        print "STARTING!!!"
        for arg in sys.argv[1:]:
            if arg.startswith("-"):
                print "skipping flag %s" % arg
            print "processing %s" % arg
            self.load_file(arg, None)
    
    def _window_created_fired(self, event):
        """The toolkit window doesn't exist yet.
        """
    
    def _window_opened_fired(self, event):
        """The toolkit window does exist here.
        """
        print "WINDOW OPENED!!! %s" % event.window.control
        import wx
        event.window.control.Bind(wx.EVT_IDLE, self._wx_on_idle)

    #### API

    def load_file(self, uri, active_task):
        service = self.get_service("peppy2.file_type.i_file_recognizer.IFileRecognizerDriver")
        print "SERVICE!!!", service
        
        from peppy2.utils.file_guess import FileGuess
        # The FileGuess loads the first part of the file and tries to identify it.
        guess = FileGuess(uri)
        
        # Attempt to classify the guess using the file recognizer service
        service.recognize(guess)
        
        possibilities = []
        for factory in self.task_factories:
            print "factory: %s" % factory.name
            if hasattr(factory.factory, "can_edit"):
                if factory.factory.can_edit(guess.metadata.mime):
                    print "  can edit: %s" % guess.metadata.mime
                    possibilities.append(factory)
        print possibilities
        if not possibilities:
            print "no editor for %s" % uri
            return
        
        best = possibilities[0]
        
        # Look for existing task in current windows
        for window in self.windows:
            print "window: %s" % window
            print "  active task: %s" % window.active_task
            if window.active_task.__class__ == best.factory:
                print "  found active task"
                window.active_task.new(guess)
                return
        
        # Not found in existing windows, so open new window with task
        tasks = [ factory.id for factory in possibilities ]
        print "no task window found: creating new layout for %s" % str(tasks)
#        window = self.create_window(TaskWindowLayout(size = (800, 600)))
        window = self.create_window(layout=TaskWindowLayout())
        print "  window=%s" % str(window)
        first = None
        for factory in possibilities:
            task = factory.factory()
            window.add_task(task)
            first = first or task
        window.activate_task(first)
        window.open()
        print "All windows: %s" % self.windows
        task.new(guess)
        metadata = guess.get_metadata()
        print guess.metadata
        print guess.metadata.mime
        print metadata
        print metadata.mime
        print dir(metadata)


    #### wx event handlers ####################################################

    def _wx_on_idle(self, evt):
        """ Called during idle time. """
        control = evt.GetEventObject()
        if control == self.active_window.control:
            #print "Processing idle on %s" % self.active_window
            self.active_window.active_task.process_idle()
        else:
            #print "Skipping idle on %s" % control
            pass