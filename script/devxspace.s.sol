// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../lib/forge-std/src/Script.sol";
import "../src/DXcoin.sol";
import "../src/DevXspace.sol";

contract devxdeploy is Script {
    DevXspace devxspace;
    DXcoin dxtoken;

    function run() public {
        uint256 key = vm.envUint("private_key");
        vm.startBroadcast(key);
        devxspace = new DevXspace(0xE6e2595f5f910c8A6c4cf42267Ca350c6BA8c054, 4, 500, 500, 2);
        dxtoken = new DXcoin("DXcoin", "DXC");
        vm.stopBroadcast();

        console.log(address(devxspace));
        console.log(address(dxtoken));
    }

}
