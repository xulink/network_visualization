#!/usr/bin/python
# coding=utf-8

import queue

class Analyzer:
    def __init__(self, point):
        self.point = point
        # 用于存id与点的kv对
        self.data = {}
        self.vis = {}

        self.dir = [[10, -10, 0, 0], [0, 0, 10, -10], [0, 0, 0, 0]]

    def sort(self):
		self.point.point_data = sorted(self.point.point_data, key = lambda x:x[1])
		num=0
		self.point.point_data[0][5]=num
		length=len(self.point.point_data)
		for i in range(1,length):
			mark=0
			if self.point.point_data[i][1][1]=='.':
				mark=2
			elif self.point.point_data[i][1][2]=='.':
				mark=3
			elif self.point.point_data[i][1][3]=='.':
				mark=4
			s=self.point.point_data[i][1][:mark]
			if self.point.point_data[i-1][1][:mark]==s :
				self.point.point_data[i][5]=num
			elif :
			    num+=1
				self.point.point_data[i][5]=num

    def cal_center_point(self):
        sum_x, sum_y, sum_z = 0, 0, 0
        for k, v in self.vis.items():
            tmp = k.split(':')
            tmp_x = float(tmp[0])
            tmp_y = float(tmp[1])
            tmp_z = float(tmp[2])

            sum_x = sum_x + tmp_x
            sum_y = sum_y + tmp_y
            sum_z = sum_z + tmp_z

        sum_x = sum_x / len(self.vis)
        sum_y = sum_y / len(self.vis)
        sum_z = sum_z / len(self.vis)

        return sum_x, sum_y, sum_z

    def balance(self):
        avg_x, avg_y, avg_z = self.cal_center_point()

        for i in range(len(self.point)):
            p = self.point[i]
            x = p['location']['x']
            y = p['location']['y']
            z = p['location']['z']
            self.point[i]['location'].update(dict(x=x-avg_x, y=y-avg_y, z=z-avg_z))

    def find_new_block(self):
        x = 0
        y = 0
        z = 0
        if self.vis == {}:
            return x, y, z

        avg_x, avg_y, avg_z = self.cal_center_point()
        min_x = dict(x=100000000000, y=0, z=0)
        min_y = dict(x=0, y=100000000000, z=0)
        min_z = dict(x=0, y=0, z=100000000000)
        max_x = dict(x=-100000000000, y=0, z=0)
        max_y = dict(x=0, y=-100000000000, z=0)
        max_z = dict(x=0, y=0, z=-100000000000)

        for k, v in self.vis.items():
            tmp = k.split(':')
            tmp_x = float(tmp[0])
            tmp_y = float(tmp[1])
            tmp_z = float(tmp[2])
            if tmp_x > max_x['x']:
                max_x.update(dict(x=tmp_x, y=tmp_y, z=tmp_z))
            if tmp_y > max_y['y']:
                max_y.update(dict(x=tmp_x, y=tmp_y, z=tmp_z))
            if tmp_z > max_z['z']:
                max_z.update(dict(x=tmp_x, y=tmp_y, z=tmp_z))

            if tmp_x < min_x['x']:
                min_x.update(dict(x=tmp_x, y=tmp_y, z=tmp_z))
            if tmp_y < min_y['y']:
                min_y.update(dict(x=tmp_x, y=tmp_y, z=tmp_z))
            if tmp_z < min_z['z']:
                min_z.update(dict(x=tmp_x, y=tmp_y, z=tmp_z))

        # 找距离最近的，尽量让中心点居中
        new_location = max_x
        dis = (avg_x - max_x['x']) ** 2 + (avg_y - max_x['y']) ** 2 + (avg_z - max_x['z']) ** 2
        for item in [max_x, max_y, max_z, min_x, min_y, min_z]:
            dis2 = (avg_x - item['x']) ** 2 + (avg_y - item['y']) ** 2 + (avg_z - item['z']) ** 2
            if dis2 < dis:
                new_location = item
                dis =dis2

        x = new_location['x']
        y = new_location['y']
        z = new_location['z']
        for i in range(4):
            nxt_x = x + self.dir[0][i] * 3
            nxt_y = y + self.dir[1][i] * 3
            nxt_z = z
            pos = str(nxt_x) + ':' + str(nxt_y) + ':' + str(nxt_z) + ':'
            if self.vis.get(pos, False):
                continue
            x, y, z = nxt_x, nxt_y, nxt_z
            break

        return x, y, z

    def genearte_location(self):
        bfs_queue = queue.Queue()

        for i, p in enumerate(self.point):
            if self.data[p['id']].get('vis', False):
                continue

            bfs_queue.put(p)
            x, y, z = self.find_new_block()
            self.point[p['id']].update({'location': dict(x=x, y=y, z=z)})
            pos = str(p['location']['x']) + ':' + str(p['location']['y']) + ':' + str(p['location']['z'])
            self.vis[pos] = True
            self.data[p['id']]['vis'] = True

            while(bfs_queue.empty() != True):
                p = bfs_queue.get()
                x = p['location']['x']
                y = p['location']['y']
                z = p['location']['z']
                for nxt_id in p['link']:
                    if self.data[nxt_id].get('vis', False):
                        continue

                    nxt_p = self.point[self.data[nxt_id]['index']]
                    bfs_queue.put(nxt_p)
                    self.data[nxt_id]['vis'] = True
                    nxt_z = 0
                    for i in range(4):
                        nxt_x = x + self.dir[0][i]
                        nxt_y = y + self.dir[1][i]
                        pos = str(nxt_x) + ':' + str(nxt_y) + ':' + str(nxt_z) + ':'
                        if self.vis.get(pos, False):
                            continue
                        self.point[nxt_id]['location'].update(dict(x=nxt_x, y=nxt_y, z=nxt_z))
                        self.vis[pos] = True
                        break


    def process(self):
        self.sort()

        for i, p in enumerate(self.point):
            self.data[p.get('id')] = dict(index=i)

        self.genearte_location()
        self.balance()
        return self.point

if __name__ == '__main__':
    analyzer = Analyzer([])
    analyzer.process()
