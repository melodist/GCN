import os
import glob
import cv2
import numpy as np
import tensorflow as tf
from datasets import data as dataset
from models.nn import GCN as ConvNet
from learning.evaluators import AccuracyEvaluator as Evaluator
from learning.utils import draw_pixel

""" 1. Load dataset """
root_dir = os.path.join('data/original/')    # FIXME
test_dir = os.path.join(root_dir, 'test')

# Set image size and number of class
IM_SIZE = (512, 512)
NUM_CLASSES = 2

# Load test set
X_test, y_test = dataset.read_data(test_dir, IM_SIZE)
test_set = dataset.DataSet(X_test, y_test)

""" 2. Set test hyperparameters """
hp_d = dict()

# FIXME: Test hyperparameters
hp_d['batch_size'] = 8

""" 3. Build graph, load weights, initialize a session and start test """
# Initialize
graph = tf.get_default_graph()
config = tf.ConfigProto()
config.gpu_options.allow_growth = True

model = ConvNet([IM_SIZE[0], IM_SIZE[1], 3], NUM_CLASSES, **hp_d)
evaluator = Evaluator()
saver = tf.train.Saver()

sess = tf.Session(graph=graph, config=config)
saver.restore(sess, './model.ckpt')    # restore learned weights
test_y_pred = model.predict(sess, test_set, **hp_d)
test_score = evaluator.score(test_set.labels, test_y_pred)

print('Test accuracy: {}'.format(test_score))

""" 4. Draw masks on image """
draw_dir = os.path.join(test_dir, 'draws') # FIXME
if not os.path.isdir(draw_dir):
    os.mkdir(draw_dir)
im_dir = os.path.join(test_dir, 'images') # FIXME
im_paths = []
im_paths.extend(glob.glob(os.path.join(im_dir, '*.png')))
test_outputs = draw_pixel(test_y_pred)
test_results = test_outputs + test_set.images
for img, im_path in zip(test_results, im_paths):
    name = im_path.split('/')[-1]
    draw_path =os.path.join(draw_dir, name)
    cv2.imwrite(draw_path, img)
