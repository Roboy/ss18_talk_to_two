from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np 



if __name__ == "__main__":

	sources_1=np.ones(50)
	sources_0=np.zeros(50)
	np.random.seed(19680801)

	while True:
		N = 50
		x = np.random.rand(N)
		y = np.random.rand(N)
		colors = np.random.rand(N)
		area = (30 * np.random.rand(N))**2  # 0 to 15 point radii

		plt.scatter(x, y, s=area, c=colors, alpha=0.5)
		plt.pause(1)
		plt.show()
		print 'drawing'
	plt.close()