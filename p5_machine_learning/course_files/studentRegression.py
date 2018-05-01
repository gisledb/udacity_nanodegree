def studentReg(ages_train, net_worths_train):
    ### import the sklearn regression module, create, and train your regression
    ### name your regression reg
    
    ### your code goes here!
    # Importing library
    from sklearn.linear_model import LinearRegression

    # Setting up regression
    reg = LinearRegression()
    # Training regression
    reg.fit(ages_train, net_worths_train)

    return reg