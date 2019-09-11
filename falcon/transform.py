# -*- coding: utf-8 -*-
"""transform.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ETw2LDZMSljEMf3v3EYYi5TTaQ6mDLze
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import tensorflow as tf

import numpy as np

import argparse
import os
import sys


def rotate(x: tf.Tensor, degrees: float) -> tf.Tensor:
  random_angles = tf.random.uniform([], minval = -(np.pi * degrees)/180, maxval = (np.pi * degrees)/180)
  rotated_image = tf.contrib.image.transform(x,tf.contrib.image.angles_to_projective_transforms(random_angles, tf.cast(tf.shape(x)[0], tf.float32), tf.cast(tf.shape(x)[1], tf.float32)))
  return rotated_image

def replace_slice(input_: tf.Tensor, replacement, begin) -> tf.Tensor:
    inp_shape = tf.shape(input_)
    size = tf.shape(replacement)
    padding = tf.stack([begin, inp_shape - (begin + size)], axis=1)
    replacement_pad = tf.pad(replacement, padding)
    mask = tf.pad(tf.ones_like(replacement, dtype=tf.bool), padding)
    return tf.where(mask, replacement_pad, input_)


def cutout(x: tf.Tensor, h: int, w: int, c: int = 3) -> tf.Tensor:
  """
  Cutout data augmentation. Randomly cuts a h by w whole in the image, and fill the whole with zeros.
  :param x: Input image.
  :param h: Height of the hole.
  :param w: Width of the hole
  :param c: Number of color channels in the image. Default: 3 (RGB).
  :return: Transformed image.
  """
  shape = tf.shape(x)
  x0 = tf.random.uniform([], 0, shape[0] + 1 - h, dtype=tf.int32, seed= None)
  y0 = tf.random.uniform([], 0, shape[1] + 1 - w, dtype=tf.int32, seed= None)
  x = replace_slice(x, tf.zeros([h, w, c]), [x0, y0, 0])
  return x


def random_flip(x: tf.Tensor) -> tf.Tensor:
  return tf.image.random_flip_left_right(x,seed=None)


def random_pad_crop(x: tf.Tensor, pad_size = 4) -> tf.Tensor:
  """
  Randomly pad the image by `pad_size` at each border (top, bottom, left, right). Then, crop the padded image to its
  original size.
  :param x: Input image.
  :param pad_size: Number of pixels to pad at each border. For example, a 32x32 image padded with 4 pixels becomes a
                   40x40 image. Then, the subsequent cropping step crops the image back to 32x32. Padding is done in
                   `reflect` mode.
  :return: Transformed image.
  """
  shape = tf.shape(x)
  x = tf.pad(x, [[pad_size, pad_size], [pad_size, pad_size], [0, 0]], mode='reflect')
  x = tf.image.random_crop(x, [shape[0], shape[1], 3])
  return x


def augment(x: tf.Tensor, func_list: []) -> tf.Tensor:
  if not func_list:
    return x
  else:
    for f in func_list:
      x = f(x)
    return x