ENCODING = 'utf-8'


class Person:
    def __init__(self, tuple):
        info = tuple[1]

        self.dn = tuple[0]
        self.uid = info['uid'][0].decode(ENCODING)
        self.cn = info['cn'][0].decode(ENCODING)
        self.homeDirectory = info['homeDirectory'][0].decode(ENCODING) if 'homeDirectory' in info else ''
        self.uidNumber = info['uidNumber'][0].decode(ENCODING) if 'uidNumber' in info else ''
        self.gidNumber = info['gidNumber'][0].decode(ENCODING) if 'gidNumber' in info else ''
        self.groupName = None

        self.groups = []

    def __eq__(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        if self.uidNumber:
            return self.uidNumber == other.uidNumber
        else:
            return self.dn == other.dn

    def full_eq(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        return (
                self.dn == other.dn and
                self.cn == other.cn and
                self.uid == other.uid and
                self.homeDirectory == other.homeDirectory and
                self.uidNumber == other.uidNumber and
                self.gidNumber == other.gidNumber and
                self.groupName == other.groupName and
                self.groups == other.groups
        )

    def __repr__(self):
        return """
            Person:
                uid: {uid}
                cn: {cn}
                homeDirectory: {homeDirectory}
                uidNumber: {uidNumber}
                gidNumber: {gidNumber}
                groupName: {groupName}
                groups: {groups}
        """.format(uid=self.uid, cn=self.cn, homeDirectory=self.homeDirectory,
                   uidNumber=self.uidNumber, gidNumber=self.gidNumber,
                   groupName=self.groupName, groups=str(self.groups))


class Group:
    def __init__(self, tuple):
        info = tuple[1]

        self.dn = tuple[0]
        self.memberUid = info.setdefault('memberUid', [])
        self.memberUid = list(map(lambda m: m.decode(ENCODING), self.memberUid))
        self.gidNumber = info['gidNumber'][0].decode(ENCODING) if 'gidNumber' in info else ''
        self.cn = info['cn'][0].decode(ENCODING)
        self.member = info['member'][0] if 'member' in info else None

    def __eq__(self, other):
        if not isinstance(other, Group):
            return NotImplemented
        return (
                self.gidNumber == other.gidNumber if self.gidNumber else self.cn == other.cn
        )

    def full_eq(self, other):
        if not isinstance(other, Group):
            return NotImplemented
        return (
                (self.gidNumber == other.gidNumber if self.gidNumber else True) and
                self.cn == other.cn
        )

    def __repr__(self):
        return """
            Group:
                memberUid: {memberUid}
                gidNumber: {gidNumber}
                cn: {cn} 
                member: {member}
        """.format(memberUid=self.memberUid, gidNumber=self.gidNumber, cn=self.cn, member=self.member)
