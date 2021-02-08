import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as colors
from mpl_toolkits import mplot3d
from astropy.modeling.models import Sersic2D


class evopt:
	"""
	A class used to optimize a function using differential evolution

	Attributes
	----------
	bounds : numpy array
		Parameter boundaries.
	paramshape : tuple
		Dimensionality of the parameter space.
	popsize : int
		Number of members of the population.
	initscale : int
		Scales the popsize used to find the initial best params.
	fittest : numpy array
		Current best-fitting model.
	bestloss : float
		Loss of the current best-fitting model.
	popshape : list
		Shape of the full array/population of vectors.
	minb : numpy array
		Array containing min value of param bounds.
	maxb : numpy array
		Array containing max value of param bounds.
	delta : numpy array
		maxb - minb
	pop_norm : numpy array
		Full population of possible solution vectors.
	pop_denorm : numpy array
		Full population of possible solution vectors, denormed to param bounds.
	"""

	def __init__(self, bounds, popsize=20, initscale=1, ):
		self.bounds = bounds
		self.paramshape = bounds.shape[:-1]
		self.popsize = popsize
		self.initscale = initscale
		self.fittest = np.array([])
		self.bestloss = 9999.0

		# create initial population of random vectors
		self.popshape = [self.popsize * self.initscale]
		self.popshape.extend(self.paramshape)
		self.minb = np.full((self.popshape), self.bounds.T[0].T)
		self.maxb = np.full((self.popshape), self.bounds.T[1].T)
		self.delta = np.fabs(self.maxb - self.minb)
		self.pop_norm = np.random.random_sample(self.popshape)
		self.pop_denorm = self.minb + (self.pop_norm * self.delta)

	def evaltt(self, *args, target, trial, model, lossfn, data):
		"""Denorms the target and trial vectors, then evaluates them."""
		
		target_denorm = self.minb[0] + (target * self.delta[0])
		trial_denorm = self.minb[0] + (trial * self.delta[0])
		target_pred = model(*args, target_denorm)
		trial_pred = model(*args, trial_denorm)
		target_fitness = lossfn(target_pred, data)
		trial_fitness = lossfn(trial_pred, data)
		return target_fitness, trial_denorm, trial_fitness

	def updateControlParams(muts, cxps, idx):
		"""Updates a vector's mutation factor and crossover probabilities."""
		
		rands = np.random.random_sample(4)
		if rands[0] < 0.1:
			muts[idx] = 0.1 + rands[1] * 0.9
		if rands[2] < 0.1:
			cxps[idx] = rands[3]

	def best1(self, fittest_id, mut, cxp, target, target_idx):
		"""Creates a trial vector to compare against the target vector."""
		
		idxs = [j for j in range(self.popsize) if j != target_idx]
		a, b = np.random.choice(idxs, 2, replace=False)
		mutvec1 = mut * (self.pop_norm[a] - self.pop_norm[b])
		doner = self.pop_norm[fittest_id] + mutvec1 
		doner = np.clip(doner, 0, 1)
		crosspoints = np.random.random_sample(self.popshape[1:]) < cxp
		trial = np.where(crosspoints, doner, target)
		return trial

	def best2(self, fittest_id, mut, cxp, target, target_idx):
		"""Creates a trial vector to compare against the target vector."""
		
		idxs = [j for j in range(self.popsize) if j != target_idx]
		a, b, c, d = np.random.choice(idxs, 4, replace=False)
		mutvec1 = mut * (self.pop_norm[a] - self.pop_norm[b])
		mutvec2 = mut * (self.pop_norm[c] - self.pop_norm[d])
		doner = self.pop_norm[fittest_id] + mutvec1 + mutvec2
		doner = np.clip(doner, 0, 1)
		crosspoints = np.random.random_sample(self.popshape[1:]) < cxp
		trial = np.where(crosspoints, doner, target)
		return trial

	def pbest1(self, pop_fitness, mut, cxp, target, target_idx, p):
		"""Creates a trial vector to compare against the target vector."""
		
		best_idxs = np.argsort(pop_fitness)[:int(self.popsize * p)]
		a = np.random.choice(best_idxs)
		idxs = [j for j in range(self.popsize) if j != target_idx]
		b, c = np.random.choice(idxs, 2, replace=False)
		mutvec1 = mut * (self.pop_norm[a] - target)
		mutvec2 = mut * (self.pop_norm[b] - self.pop_norm[c])
		doner = target + mutvec1 + mutvec2
		doner = np.clip(doner, 0, 1)
		crosspoints = np.random.random_sample(self.popshape[1:]) < cxp
		trial = np.where(crosspoints, doner, target)
		return trial

	def diffevo(self, *args, model, lossfn, data, mut=0.5, cxp=0.8, iters=100):
		"""
		Uses one of the trial-vector-creating functions to optimize a set of
		model parameters.
		"""
		
		# save the fittest members of init population
		predictions = np.asarray([model(*args, f) for f in self.pop_denorm])
		pop_fitness = np.asarray([rms(f, data) for f in predictions])
		survivor_ids = np.argsort(pop_fitness)[:self.popsize]
		self.pop_denorm = self.pop_denorm[survivor_ids]
		pop_fitness = pop_fitness[survivor_ids]
		fittest_id = np.argmin(pop_fitness)
		self.fittest = self.pop_denorm[fittest_id]
		self.bestloss = pop_fitness[fittest_id]

		for iter in range(iters):
			for i in range(self.popsize):
				# the target vector is the vector we'll consider replacing with a trial vector
				target = self.pop_norm[i]
				trial = evopt.best1(self, fittest_id, mut, cxp, target, i)
				target_fitness, trial_denorm, trial_fitness = evopt.evaltt(self, *args, target=target, trial=trial, model=model, lossfn=lossfn, data=data)

				# if the trial vector is fitter than the target vector, replace the target vec with the trial vec in the population
				if trial_fitness < target_fitness:
					self.pop_norm[i] = trial
					self.pop_denorm[i] = trial_denorm
					pop_fitness[i] = trial_fitness

				# if the trial vector is fitter than the fittest vector, replace it
				if trial_fitness < self.bestloss:
					self.fittest = trial_denorm
					self.bestloss = trial_fitness
					fittest_id = i

			# works best as a generator
			yield self.pop_denorm, self.fittest
		
		print("Final loss: " + str(self.bestloss))

	def jade(self, *args, model, lossfn, data, iters, p):
		"""
		Uses one of the trial-vector-creating functions to optimize a set of
		model parameters. Unlike vanilla diffevo, jade allows the mutation factor
		and crossover probability to evolve.
		"""

		# init mut and cxp values
		muts = np.random.random_sample(self.popsize)
		cxps = np.random.random_sample(self.popsize)

		# save the fittest members of init population
		predictions = np.asarray([model(*args, f) for f in self.pop_denorm])
		pop_fitness = np.asarray([rms(f, data) for f in predictions])
		survivor_ids = np.argsort(pop_fitness)[:self.popsize]
		self.pop_denorm = self.pop_denorm[survivor_ids]
		pop_fitness = pop_fitness[survivor_ids]
		fittest_id = np.argmin(pop_fitness)
		self.fittest = self.pop_denorm[fittest_id]
		self.bestloss = pop_fitness[fittest_id]

		for iter in range(iters):
			for i in range(self.popsize):
				# the target vector is the vector we'll consider replacing with a trial vector
				mut = muts[i]
				cxp = cxps[i]
				target = self.pop_norm[i]
				trial = evopt.pbest1(self, pop_fitness, mut, cxp, target, i, p)
				target_fitness, trial_denorm, trial_fitness = evopt.evaltt(self, *args, target=target, trial=trial, model=model, lossfn=lossfn, data=data)

				# if the trial vector is fitter than the target vector, replace the target vec with the trial vec in the population
				if trial_fitness < target_fitness:
					self.pop_norm[i] = trial
					self.pop_denorm[i] = trial_denorm
					pop_fitness[i] = trial_fitness
					evopt.updateControlParams(muts, cxps, i)
					

				# if the trial vector is fitter than the fittest vector, replace it
				if trial_fitness < self.bestloss:
					self.fittest = trial_denorm
					self.bestloss = trial_fitness
					fittest_id = i

			# works best as a generator
			yield self.pop_denorm, self.fittest
		
		print("Final loss: " + str(self.bestloss))




# example usage: optimizing a 2d sersic function to recover the physical
# parameters of a mock high-redshift galaxy.

def model(x, y, w):
	comp1 = Sersic2D.evaluate(
		x,y, w[0,10], w[0,0], w[0,1], w[0,2], w[0,3], w[0,4], w[0,5]
	)
	comp2 = Sersic2D.evaluate(
		x,y, w[0,11], w[0,6], w[0,7], w[0,2], w[0,3], w[0,8], w[0,9]
	)
	return comp1 + comp2

def rms(p, z):
	return np.sqrt(np.sum((p - z)**2) / len(z))


bounds = [
	(5,10),         #0 r_e1
	(4,8),          #1 n1
	(45, 55),       #2 x
	(45, 55),       #3 y
	(0,0.99),       #4 e1
	(0, 2*np.pi),   #5 theta1
	(10,50),        #6 r_e2
	(1,4),          #7 n2
	(0,0.99),       #8 e2
	(0, 2*np.pi),   #9 theta2
	(0, 3),         #10 I1
	(0, 3),         #11 I2
]
bounds = np.array([bounds])
opto = evopt(bounds, popsize=100, initscale=1)
xmin, xmax = (0,100)
ymin, ymax = (0,100)
x = np.linspace(xmin,xmax,100)
y = np.linspace(ymin,ymax,100)
X, Y = np.meshgrid(x,y)
x = X.flatten()
y = Y.flatten()

n1 = np.random.randint(4,8)
n2 = np.random.randint(1,4)
x1 = np.random.randint(45,55)
y1 = np.random.randint(45,55)
r1 = np.random.randint(5,10)
r2 = np.random.randint(10,50)
I1 = np.random.randint(0,3)
I2 = np.random.randint(0,3)
print(r1, n1, x1, y1)
print(r2, n2, I1, I2)
Z = Sersic2D.evaluate(X,Y, I1, r1, n1, x1, y1, 0, -1) + Sersic2D.evaluate(X,Y, I2, r2, n2, x1, y1, 0.69, -1) + np.random.normal(0, 0.3, (100,100))


results = []
fit_list = []
iters = 50 
for f,g in opto.diffevo(X,Y, model=model, lossfn=rms, data=Z, iters=iters):
	results.append(f.copy()) # need .copy() to append correctly
	fit_list.append(g.copy())
print(fit_list[0])
print(fit_list[-1])


plt.style.use('Solarize_Light2')
plt.rcParams['axes.grid'] = False
fig, ax = plt.subplots(
	1,2,
	figsize=(8,5),
	dpi=120,
)
fig.tight_layout()
log_fgal = np.log10(np.abs(Z))
ax[0].imshow(log_fgal, origin='lower', interpolation='nearest', vmin=-1, vmax=1)
def animate(i):
	ax[1].clear()
	best_fit = fit_list[i]
	data = model(X,Y, best_fit)
	resid = Z - data
	log_img = np.log10(np.abs(resid))
	ax[1].imshow(resid, origin='lower', interpolation='nearest', vmin=-2, vmax=2)
anim = animation.FuncAnimation(fig, animate, frames=len(results), interval=200)
#writer = animation.PillowWriter(fps=10)
#anim.save('sersic-resid.gif', writer=writer)
plt.show()
