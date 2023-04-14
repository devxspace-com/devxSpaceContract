// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../src/DevXspace.sol";
import "../src/DXcoin.sol";
import "../src/escrow.sol";

contract DevXspaceTest is Test {
    DevXspace devxspace;
    TokenERC20 devxcoin;
    EscrowByAgentV2 escrow;


    function setUp() public {
        vm.startPrank(0xEd5DfD4d3E4d12eD7D0C5A9224772E4e33eec155);
       devxcoin = new TokenERC20("DXcoin", "DXC");
       escrow = new EscrowByAgentV2(500, 500, 2);
       devxspace = new DevXspace(0x9B69F998b2a2b20FF54a575Bd5fB90A5D71656C1, address(escrow), 0);
       devxcoin.mint(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C, 5 ether);  
        vm.stopPrank();
    }

    function testcreateGig() public {
        vm.prank(0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353);
        devxspace.createGig(1 ether);
        // devxspace.gigDetails(0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353);
        vm.prank(0xff78e3146d0a3Be185A501DA5EeD0172d5400189);
        devxspace.createGig(1 ether);
    }

    function testHireAcceptReject() public {
        testcreateGig();
        vm.prank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
        devxspace.hire(0);
        vm.startPrank(0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353);
        devxspace.viewOffer(0);
        devxspace.AcceptOrReject(0, 1);
        vm.stopPrank();
    }

    function testPaymentWithETH() public {
        testHireAcceptReject();
        vm.prank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
        vm.deal(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C, 50 ether);
        devxspace.payWithEth{value: 1 ether}(0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353, 0);
    }

    // function testPaymentWithToken() public {
    //     testHireAcceptReject();
    //     vm.startPrank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
    //     devxcoin.approve(address(devxspace), 5 ether);
    //     devxspace.payWithToken(IERC20(devxcoin),0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353, 0);
    //     console.log(devxcoin.balanceOf(address(devxspace)));
    //     vm.stopPrank();
    // }

    // function testRelease() public {
    //     testPaymentWithETH();
    //     vm.prank(0x9B69F998b2a2b20FF54a575Bd5fB90A5D71656C1);
    //     escrow.release(0);
    // }

    function testApproveCancel() public {
        testPaymentWithETH();
        vm.warp(3 days);
        vm.prank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
        devxspace.approveCancel(0);
        vm.prank(0x7a5863fe6A65377A7cd3F2A6d417F489D9DCF353);
        escrow.approveCancel(0);
        vm.prank(0x9B69F998b2a2b20FF54a575Bd5fB90A5D71656C1);
        escrow.approveCancel(0);
    }

    function testCancel() public {
        testApproveCancel();
        vm.prank(0x2e767b4A3416Ef16458355EFAcec7d3228Cec08C);
        devxspace.buyerCancel(0);
    }

}
