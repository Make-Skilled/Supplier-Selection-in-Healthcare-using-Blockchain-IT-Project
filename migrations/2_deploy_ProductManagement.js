const productManagement=artifacts.require("ProductManagement");

module.exports=function(deployer){
    deployer.deploy(productManagement);
}