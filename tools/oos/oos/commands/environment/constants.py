SUPPORT_PROVIDER = ['huaweicloud',]

OE_OS_RELEASE = {
    '20.03-lts-sp1': ['train'],
    '20.03-lts-sp2': ['rocky', 'queens'],
    '20.03-lts-sp3': ['rocky', 'queens', 'train'],
    '22.03-lts': ['train', 'wallaby'],
    '22.09': ['yoga']
}

FLAVOR_MAPPING = {
    'small_x86': 'c6.large.2',
    'medium_x86': 'c6.xlarge.2',
    'large_x86': 'c6.2xlarge.2',
    'small_aarch64': 'kc1.large.2',
    'medium_aarch64': 'kc1.xlarge.2',
    'large_aarch64': 'kc1.2xlarge.2'
}

TABLE_COLUMN = ['Provider', 'Name', 'UUID', 'IP', 'Flavor', 'openEuler_release', 'OpenStack_release', 'create_time']

OPENEULER_DEFAULT_USER = "root"
OPENEULER_DEFAULT_PASSWORD = "openEuler12#$"
