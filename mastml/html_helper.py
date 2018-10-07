"""
Module for generating the nice collected index.html file,
with best/worst plots, links to statistics, and more.
"""

from os.path import join, relpath
from time import gmtime, strftime
from dominate import document
from dominate.tags import *

import logging
import os

log = logging.getLogger('mastml')


def make_html(outdir):
    " Create the main index.html file "
    with document(title='MASTML') as doc:
        # title and date
        h1('MAterial Science Tools - Machine Learning')
        h4(strftime("%Y-%m-%d %H:%M:%S", gmtime()))

        # link to error log
        # if errors_present:
        #    p('You have errors! check ', make_link(error_log))

        combos = list()
        link_sections = list()
        # favorites = dict()

        for root, dirs, files in os.walk(outdir):
            '''
            find a folder that contains split_ folder.
            For example,
            results/StandardScaler/SelectKBest/LinearRegression/KFold
            '''
            for d in dirs:
                if d.startswith('split_0'):
                    combos.append(root)

            # extract links to important csvs and conf
            for f in files:
                csv_whitelist = [
                                 'clusters.csv',
                                 'generated_features.csv',
                                 'generated_features_no_constant_columns.csv',
                                 'grouped.csv',
                                 'input_data_statistics.csv',
                                 'normalized.csv',
                                 'selected.csv',
                                 ]

                ext = os.path.splitext(f)[1]
                if f in csv_whitelist or ext in ['.conf', '.log']:
                    link_sections.append(join(root, f))
                    # simple_section(join(root, f), outdir)

        h1('Files')
        for path in link_sections:
            simple_section(path, outdir)

        h1('Plots')

        # show all the images
        for f in os.listdir(outdir):
            if f.endswith('.png'):
                make_image(f, f)

        for combo in combos:
            # come up with a good section title
            path = os.path.normpath(relpath(combo, outdir))
            paths = path.split(os.sep)
            title = " - ".join(paths)
            h2(title)

            # find the best worst overlay
            for fname in os.listdir(combo):
                if fname.endswith('.png'):
                    # probably best_worst overlay
                    h3(os.path.splitext(fname)[0])
                    make_image(relpath(join(combo, fname), outdir), fname)
                    br()

            # find the split_0 split_1 etc bs stuff
            for fname in os.listdir(combo):
                if fname.startswith('split_'):
                    show_combo(join(combo, fname), outdir)

    with open(join(outdir, 'index.html'), 'w') as f:
        f.write(doc.render())

    log.info('wrote ' + join(outdir, 'index.html'))


def show_combo(combo_dir, outdir):
    " Add one combo to the output html "
    # collect test image, train image, and other file links
    links = list()
    train_images = list()
    test_images = list()
    for f in os.listdir(combo_dir):
        if is_train_image(f):
            train_images.append(join(combo_dir, f))
        elif is_test_image(f):
            test_images.append(join(combo_dir, f))
        else:
            links.append(join(combo_dir, f))

    # have a header for split_0 split_1 etc
    h2(combo_dir.split(os.sep)[-1])

    # loop seperately so we can control order
    for train_image, test_image in zip(
                                       sorted(train_images),
                                       sorted(test_images)
                                       ):

        make_image(relpath(train_image, outdir), 'train')
        make_image(relpath(test_image, outdir), 'test')
        br()
        br()

    h3('links')
    for l in links:
        make_link(relpath(l, outdir))
        span('  ')


def simple_section(filepath, outdir):
    " Create a section for a combo "
    path = os.path.normpath(relpath(filepath, outdir))
    paths = path.split(os.sep)
    title = " - ".join(paths)
    a(b(title))
    make_link(relpath(filepath, outdir))
    br()


def make_link(href):
    " Make a link where text is filename of href "
    return a(os.path.basename(href), href=href, style='padding-left: 15px;')


def make_image(src, title=None):
    " Show an image in fixed width "
    d = div(style='display:inline-block;', _class='photo')
    if title:
        d += h4(title)
        # d += p(a(title))
    d += img(src=src, height='200')


def is_train_image(path):
    basename = os.path.basename(path)
    return os.path.splitext(basename)[1] == '.png' and 'train' in basename


def is_test_image(path):
    basename = os.path.basename(path)
    return os.path.splitext(basename)[1] == '.png' and 'test' in basename
