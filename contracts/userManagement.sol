// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

contract userManagement {
  struct User{
    address _userAddress; // Mandatory
    string _userName;
    string _userPassword;
    string _userRole; // Mandatory
    string _userEmail;
    bool _exist;
  }

  mapping(address=>User) users; // user wallet address is pointing a structure of user -> users[_users[0]]
  mapping(string=>User) usernames; // _usernames[username]
  address[] userAddresses; // user dynamic array of wallet addresses, _users[0], _users[1]


  // It will create an account of user
  function userSignUp(address wallet,string memory username,string memory password,string memory role,string memory email) public {
    require(!users[wallet]._exist,"Already exist"); // require condition should be always false
    require(!usernames[username]._exist,"Already username taken"); 

    // Structure Member
    User memory new_user=User(wallet,username,password,role,email,true);
    users[wallet]=new_user;
    usernames[username]=new_user; // new_user is a structure of records
    userAddresses.push(wallet); // it will push wallet address
  }

  // It will return all the registered Users
  function viewAllUsers() public view returns(User[] memory){
    User[] memory _userArray = new User[] (userAddresses.length); // 100 chairs (empty)
    // empty structures create -> the length of userAddress (1)

    for (uint256 i = 0; i < userAddresses.length; i++) { // 0<1 // 100 students one-by-one seating
            _userArray[i] = users[userAddresses[i]]; // users[wallet]
    }

    return _userArray; 
  }

  // It will return only one record of user based on username
  function viewUserByUsername(string memory username) public view returns(User memory) {
    require(usernames[username]._exist,"No account with that username"); // true
    return usernames[username];
  }

  // It will return only one record of user based on wallet
  function viewUserByWallet(address wallet) public view returns(User memory) {
    require(users[wallet]._exist,"No account with that wallet");
    return users[wallet];
  }

  // It will validate the login details of user
  function userLogin(string memory username,string memory password) public view returns(bool){
    require(usernames[username]._exist,"No account with that username"); 

    if(keccak256(bytes(username))==keccak256(bytes(usernames[username]._userName))){
      if(keccak256(bytes(password))==keccak256(bytes(usernames[username]._userPassword))){
        return true;
      } else {
        return false;
      }
    } else {
      return false;
    }
  }
}
