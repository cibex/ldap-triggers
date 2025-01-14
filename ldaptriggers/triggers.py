ENCODING = 'utf-8'

import os
from subprocess import Popen, PIPE

from .params import TRIGGERS_PATH
from .log import get_logger


def trigger(deleted_people, added_people, deleted_groups, added_groups, modified_people, modified_groups):
    """
    Fetches the stored triggers in TRIGGERS_PATH and executes them.
    :param deleted_people: Array
    :param added_people: Array
    :param deleted_groups: Array
    :param added_groups: Array
    :param modified_people: Array
    :param modified_groups: Array
    :return:
    """
    logger = get_logger()

    triggers = os.listdir(TRIGGERS_PATH)

    # TODO: make this more efficient
    add_people_triggers = list(filter(lambda f: f.startswith("add_people_"), triggers))
    delete_people_triggers = list(filter(lambda f: f.startswith("delete_people_"), triggers))
    modify_people_triggers = list(filter(lambda f: f.startswith("modify_people_"), triggers))

    add_groups_triggers = list(filter(lambda f: f.startswith("add_groups_"), triggers))
    delete_groups_triggers = list(filter(lambda f: f.startswith("delete_groups_"), triggers))
    modify_groups_triggers = list(filter(lambda f: f.startswith("modify_groups_"), triggers))

    get_param_person = lambda p: [str(p.uid)]
    get_param_group = lambda g: [str(g.cn), str(g.gidNumber)]
    get_param_person_group = lambda p: [str(p.uid), str(p.groupName)] + p.groups

    get_env_person = lambda p: {'person_cn': p.cn, 'person_dn': p.dn}
    get_env_group = lambda g: {'group_cn': g.cn, 'group_dn': g.dn}
    get_env_person_group = lambda p: {'person_cn': p.cn, 'person_dn': p.dn}

    def call_trigger(entities, triggers, get_param, get_env):
        logger.debug(f"call_trigger: entities:'{entities}' triggers:'{triggers}' get_param:'{get_param}' ")
        for e in entities:
            for t in triggers:
                trigger_env = os.environ.copy()
                trigger_env.update(get_env(e))
                p = Popen([TRIGGERS_PATH + t] + get_param(e), stdin=PIPE, stdout=PIPE, stderr=PIPE, env=trigger_env)
                output, err = p.communicate("")
                rc = p.returncode
                if rc != 0:
                    logger.error(t + ' | ' + str(get_param(e)) + ' | ' + str(get_env(e))
                                 + ' | ' + str(rc) + ' | ' + err.decode(ENCODING))
                else:
                    logger.info(t + ' | ' + str(get_param(e)) + ' | ' + str(get_env(e))
                                + ' | ' + str(rc) + ' | ' + output.decode(ENCODING))

    call_trigger(deleted_people, delete_people_triggers, get_param_person, get_env_person)

    call_trigger(deleted_groups, delete_groups_triggers, get_param_group, get_env_group)
    call_trigger(added_groups, add_groups_triggers, get_param_group, get_env_group)
    call_trigger(modified_groups, modify_groups_triggers, get_param_group, get_env_group)

    call_trigger(added_people, add_people_triggers, get_param_person_group, get_env_person_group)
    call_trigger(modified_people, modify_people_triggers, get_param_person_group, get_env_person_group)
