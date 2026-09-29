import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df=pd.read_csv('/home/sanxi/machine learning theory and engineering/data generation/data.csv')


X=df['X'].to_numpy()
Y=df['Y'].to_numpy()
A=np.column_stack([X**2,X,np.ones(X.size)])

w=np.linalg.inv(A.T@A)@A.T@Y
print(w)
x=np.linspace(-100,100,200)
y=w[0]*x**2+w[1]*x+w[2]
plt.scatter(X,Y)
plt.plot(x,y,color='red')

plt.show()


