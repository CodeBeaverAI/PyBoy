#
# License: See LICENSE.md file
# GitHub: https://github.com/Baekalfen/PyBoy
#
"""
This class gives access to the sound buffer of PyBoy.
"""

import numpy as np

from pyboy import utils
from pyboy.logging import get_logger

logger = get_logger(__name__)


class Sound:
    """
    As part of the emulation, we generate a sound buffer for each frame on the screen. This class has several helper
    methods to make it possible to read this buffer out.

    Remember to enable sound when starting `pyboy = PyBoy(..., sound=True)`.

    When the game enables/disables the LCD, the timing will be shorter than 70224 emulated cycles. Therefore the sound
    buffer will also be shorter than 16.667ms (60 FPS).
    """

    def __init__(self, mb):
        self.mb = mb

        self.sample_rate = self.mb.sound.sample_rate
        """
        Read-only. Changing this, will not change the sample rate. See `PyBoy` constructor instead.

        The sample rate is reported per second, while the frame rate of the Game Boy is ~60 frame per second.
        So expect the sound buffer to have 1/60 of this value in the buffer after every frame. Although it will
        fluctuate. See `Sound.ndarray`.

        Returns
        -------
        int:
            The sample rate in Hz (samples per second)
        """

        self.raw_buffer_format = self.mb.sound.buffer_format
        """
        Returns the color format of the raw sound buffer. **This format is subject to change.**

        See how to interpret the format on: https://docs.python.org/3/library/struct.html#format-characters

        Example:
        ```python
        >>> pyboy.sound.raw_buffer_format
        'b'
        >>> sound_buffer = array(pyboy.sound.buffer_format, pyboy.sound.raw_buffer[:pyboy.sound.raw_buffer_head])
        >>> sound_buffer[:10]

        ```

        Returns
        -------
        str:
            Color format of the raw screen buffer. E.g. 'RGBA'.
        """
        self.raw_buffer = self.mb.sound.audiobuffer
        """
        Provides a raw, unfiltered `memoryview` object with the data from sound buffer. Check
        `Sound.raw_buffer_format` to see which dataformat is used. **The returned type and dataformat are
        subject to change.** The sound buffer is in stereo format, so the odd indexes are the left channel,
        and even indexes are the right channel.

        Use this, only if you need to bypass the overhead of `Sound.ndarray`.

        Be aware to use the `Sound.raw_buffer_head`, as not all 'frames' are of equal length.

        Example:
        ```python
        >>> sound_buffer = array(pyboy.sound.buffer_format, pyboy.sound.raw_buffer[:pyboy.sound.raw_buffer_head])
        >>> sound_buffer[:10]
        ```

        Returns
        -------
        memoryview:
            memoryview of sound data.
        """

        self.raw_ndarray = None
        """
        ndarray
        """
        if self.mb.sound.enabled:
            self.raw_ndarray = np.frombuffer(
                self.mb.sound.audiobuffer,
                dtype=np.int8,
            ).reshape(self.mb.sound.samples_per_frame + 2, 2)  # +1 for rounding error
        else:
            self.raw_ndarray = utils.SoundEnabledError()

    @property
    def raw_buffer_head(self):
        """
        This returns the

        See the explanation at the top of the page.
        """
        return self.mb.sound.audiobuffer_head

    @property
    def ndarray(self):
        """
        References the sound data in NumPy format. **Remember to copy this object** if you intend to store it.
        The backing buffer will update, but it will be the same `ndarray` object.

        The format is given by `pyboy.api.sound.Sound.raw_buffer_format`. The sound buffer is in stereo format,
        so the odd indexes are the left channel, and even indexes are the right channel.

        This property returns an `ndarray` that is already accounting for the changing length of the sound buffer.
        See the explanation at the top of the page.

        Example:
        ```python
        >>> pyboy.screen.ndarray.shape
        (144, 160, 4)
        >>> # Display "P" on screen from the PyBoy bootrom
        >>> pyboy.screen.ndarray[66:80,64:72,0]
        array([[255, 255, 255, 255, 255, 255, 255, 255],
               [255, 255, 255, 255, 255, 255, 255, 255]], dtype=uint8)

        ```

        Returns
        -------
        numpy.ndarray:
            Screendata in `ndarray` of bytes with shape (144, 160, 4)
        """
        if self.mb.sound.enabled:
            return self.raw_ndarray[: self.mb.sound.audiobuffer_head]
        else:
            raise utils.PyBoyFeatureDisabledError("Sound is not enabled!")
