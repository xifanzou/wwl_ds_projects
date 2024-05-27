## 定位相关csv的说明

#### 文件说明

- localization2_gnss_pose.csv：GPS定位输出
- localization2_localization_odom.csv：融合定位输出
- localization2_correct_pose_by_wall.csv：平面定位输出
- localization2_container_pose.csv：集装箱匹配定位输出
- localization2_qc_match_pose.csv：岸桥匹配定位输出
- localization2_optimized_pose.csv：landmark匹配定位输出
- localization2_magnetic_nail.csv：磁钉定位输出
- localization2_correct_pose_by_lane.csv：车道线匹配定位输出

#### 表头说明

stamp：时间戳，单位秒

_x：该定位源的原始横坐标，单位米

_y：该定位源的原始纵坐标，单位米

_updated\_pose_x：该定位源经过滤波后的横坐标，单位米

_updated\_pose_y：该定位源经过滤波后的纵坐标，单位米

gnss_fsm_status：判断gps是否可用，1为可以用，0为不可用

gnss_base_vx：车速，单位m/s

#### 其他说明

1. qpilot_version：2.17.11
2. 各定位源仅在可被观测/有效时才记录数据





