import fnmatch
import glob
import logging
import os

from .api import API


logger = logging.getLogger('crowdin')


def is_dir(name):
    return name[-1] == '/'


def push_dir(api, localization, info,  include_source):
    structure_changed = False
    remote_path = localization['remote_path']
    if not is_dir(remote_path):
        logger.warning(
            "source_path returns multiple files but remote_path[{0}] "
            "is not a directory".format(remote_path)
        )
        return

    # remove trailing slash
    dirs = remote_path.split('/')[:-1]

    for index in range(len(dirs)):
        name = "/".join(dirs[:index + 1])
        if not api.exists(name, info):
            api.mkdir(name)
            structure_changed = True

    if structure_changed:
        info = api.info()

    source_files = glob.glob(localization['source_path'])

    excluded = localization.get('excluded', "").split(",")
    for source_file in source_files:
        file_name = os.path.split(source_file)[-1]
        if excluded and \
                [True for p in excluded if fnmatch.fnmatch(file_name, p)]:
            continue
        remote_file = os.path.join(remote_path, file_name)

        # Upload reference translations
        api.put(source_file, remote_file, info)

        if not include_source:
            continue

        # Upload local translations
        for lang, path in localization['target_langs'].items():

            if not is_dir(path):
                logger.warning(
                    "source_path returns multiple files but target_langs[{0}] "
                    "is not a directory".format(path)
                )
            lang_src_file = os.path.join(path, file_name)
            if os.path.exists(lang_src_file):
                api.put(lang_src_file, remote_file, info, lang=lang)
            else:
                logger.debug(
                    "Non-existing local {0} translation, skipping".format(lang)
                )
    return info


def push_file(api, localization, info, include_source):

    structure_changed = False
    dirs = localization['remote_path'].split('/')[:-1]
    for index in range(len(dirs)):
        name = "/".join(dirs[:index + 1])
        if not api.exists(name, info):
            api.mkdir(name)
            structure_changed = True

    if structure_changed:
        info = api.info()

    # Upload reference translations
    api.put(localization['source_path'],
            localization['remote_path'], info)

    if not include_source:
        return

    # Upload local translations
    for lang, path in localization['target_langs'].items():
        if os.path.exists(path):
            api.put(path, localization['remote_path'], info, lang=lang)
        else:
            logger.debug(
                "Inexisting local {0} translation, skipping".format(lang)
            )
    return info


def push(conf, include_source):
    api = API(project_name=conf['project_name'], api_key=conf['api_key'])
    info = api.info()

    for localization in conf['localizations']:
        if '*' in localization['source_path']:
            info = push_dir(api, localization, info, include_source)
        else:
            info = push_file(api, localization, info, include_source)


def pull_file(api, localization, translations):
    for language, path in localization['target_langs'].items():

        zip_path = '{0}/{1}'.format(language, localization['remote_path'])

        try:
            translated = translations.read(zip_path)
        except KeyError:
            logger.info("No {0} translation found".format(language))
            continue

        directory = os.path.dirname(path)
        if not os.path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError as ex:
                logging.error(ex)
                if ex.errno != 17:
                    raise
        logger.info("Writing {0}".format(path))
        with open(path, 'wb') as f:
            f.write(translated)


def pull_dir(api, localization, translations):

    for language, base_path in localization['target_langs'].items():
        if not is_dir(base_path):
            logger.warning(
                "source_path returns multiple files but target_langs[{0}] "
                "is not a directory".format(base_path)
            )
            return

        for zip_name in translations.namelist():
            if zip_name.endswith('/'):
                # don't care about folders, they will be created with
                # os.makedirs later
                continue
            base_dir, file_name = os.path.split(zip_name)
            base_dir = "{0}/".format(base_dir)
            zip_path = '{0}/{1}'.format(language, localization['remote_path'])
            # is in remote path declaration and
            if base_dir == zip_path:
                try:
                    translated = translations.read(zip_name)
                except KeyError:
                    logger.info("No {0} translation found".format(language))
                    continue
                try:
                    os.makedirs(base_path)
                except OSError:
                    pass
                target_file = "{0}{1}".format(base_path, file_name)
                logger.info("Writing {0}".format(target_file))
                with open(target_file, 'wb') as f:
                    f.write(translated)


def pull(conf):
    api = API(project_name=conf['project_name'], api_key=conf['api_key'])

    api.export()

    translations = api.translations()

    for localization in conf['localizations']:
        if '*' in localization['source_path']:
            pull_dir(api, localization, translations)
        else:
            pull_file(api, localization, translations)
