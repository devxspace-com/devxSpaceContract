// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "../lib/forge-std/src/Script.sol";
import "../src/DXcoin.sol";
import "../src/DevXspace.sol";

contract RewardScript is Script {
    DevXspace devxspace;
    DXcoin dxtoken;

    function run() public {
        devxspace = new DevXspace(0x122a5f5A90B74bE97DaED67680347b12C6178F22, 4, 500, 500, 2);
        dxtoken = new DXcoin("DXcoin", "DXC");
    }

}
