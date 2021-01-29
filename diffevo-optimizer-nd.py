import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits import mplot3d
from astropy.modeling.models import Sersic2D



def diffEvo(*args, model, lossfn, bounds, data, popsize=20, paramshape=(1,5), mut=0.5, cxp=0.8, iters=100):

	# create a population of random vectors
	popshape = [popsize]
	popshape.extend(paramshape)
	pop_norm = np.random.random_sample(popshape)
	minb = np.full((popshape), bounds[0])
	maxb = np.full((popshape), bounds[1])
	delta = np.fabs(maxb - minb)
	pop_denorm = minb + (pop_norm * delta)

	# get fittest member of init population
	predictions = np.asarray([model(*args, f) for f in pop_denorm])
	pop_fitness = [rms(f, z) for f in predictions]
	fittest_id = np.argmin(pop_fitness)
	fittest = pop_denorm[fittest_id]
	best_fitness = pop_fitness[fittest_id]

	for iter in range(iters):
		for i in range(popsize):
			# the target vector is the vector we'll consider replacing with a trial vector
			target = pop_norm[i]

			# compose a doner vector from three non-target vectors
			idxs = [j for j in range(popsize) if j != i]
			a, b, c = np.random.choice(idxs, 3, replace=False)
			doner = pop_norm[fittest_id] + mut * (pop_norm[b] - pop_norm[c])
			doner = np.clip(doner, 0, 1)

			# compose a trial vector by randomly replacing elements in the target vector with elements from the donor vector
			crosspoints = np.random.random_sample(popshape[1:]) < cxp
			trial = np.where(crosspoints, doner, target)

			# denorm the target and trial vector, then evaluate them
			target_denorm = minb[0] + (target * delta[0])
			trial_denorm = minb[0] + (trial * delta[0])
			target_pred = model(*args, target_denorm)
			trial_pred = model(*args, trial_denorm)
			target_fitness = rms(target_pred, z)
			trial_fitness = rms(trial_pred, z)

			# if the trial vector is fitter than the target vector, replace the target vec with the trial vec in the population
			if trial_fitness < target_fitness:
				pop_norm[i] = trial
				pop_denorm[i] = trial_denorm
				pop_fitness[i] = trial_fitness

			# if the trial vector is fitter than the fittest vector, replace it
			if trial_fitness < best_fitness:
				fittest = trial_denorm
				best_fitness = trial_fitness
				fittest_id = i

		# works best as a generator
		yield pop_denorm, fittest
	
	print("Final best_fitness: " + str(best_fitness))

def model(x, y, w):
	return np.polynomial.legendre.legval2d(x, y, w) 

def rms(p, z):
	return np.sqrt(np.sum((p - z)**2) / len(z))


bounds = (-10,10) 
paramshape = (4,4)
x = np.linspace(-1,1,25)
y = np.linspace(-1,1,25)
x, y = np.meshgrid(x,y)
x = x.flatten()
y = y.flatten()
z = x**2 + y**2 


results = []
fit_list = []
iters = 100
for f,g in diffEvo(x,y, model=model, lossfn=rms, bounds=bounds, data=z, popsize=50, paramshape=paramshape, iters=iters):
	results.append(f.copy()) # need .copy() to append correctly
	fit_list.append(g.copy())


plt.style.use('Solarize_Light2')
fig, ax = plt.subplots(
	1,1,
	figsize=(7,5),
	dpi=120,
)
ax = plt.axes(projection='3d')
def animate(i):
	ax.clear()
	ax.set_zlim([0,2])
	ax.scatter3D(x,y,z)
	pop = results[i]
	best_fit = fit_list[i]
	data = model(x,y, best_fit)
	ax.scatter3D(x,y, data, c='xkcd:black', alpha=1, lw=3)
anim = animation.FuncAnimation(fig, animate, frames=iters, interval=100)
#writer = animation.PillowWriter(fps=10)
#anim.save('2dyeah.gif', writer=writer)
plt.show()