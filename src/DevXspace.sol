// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
import "../lib/openzeppelin-contracts/contracts/utils/Counters.sol";
import "lib/chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol";
import "src/interface.sol/Iescrow.sol";
//creates gig details
//allows hire
//can mark job completed
//allows freelancer to accept
//notifies employer when job is done
//notifies agents when work is done
//
contract DevXspace {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;
    Counters.Counter private AgentIDCounter;
    using SafeCast for int256;
    struct SellerDetails {
        bool sellerStatus;
        address addr;
        uint gigID;
        bool offer;
        bool accepted;
        uint price; 
        bool agentApproval; 
    }
    struct AgentDetails {
        mapping(address => bool) agentStatus;
        mapping(uint => bool) selected;
        uint[] moderations;
    }
    struct BuyerInformation {
        uint hiredGigID;
        address buyerAddress;
    }

    address admin;
    mapping(uint => SellerDetails) Seller;
    mapping(uint => BuyerInformation) buyer;
    mapping(address => AgentDetails) AgentTorelease;
    AggregatorV3Interface internal ETHusdpriceFeed;
    address[] AllSellers;
    address[] agents;
    uint agentIDNumber;
    IEscrowByAgent Escrow;
    uint private nonce;

    event deposit(address sender, address recipient, address agent, uint gigID);

constructor(address _agents, address _escrow, uint _nonce ){
    agents.push(_agents);
    AgentTorelease[_agents].agentStatus[_agents] = true;
    Escrow = IEscrowByAgent(_escrow);
    nonce = _nonce;
    admin = msg.sender;
    ETHusdpriceFeed = AggregatorV3Interface(0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419);
}

    function createGig(uint _price) public {
        uint id = _tokenIdCounter.current();
        SellerDetails storage a = Seller[id];
        a.sellerStatus = true;
        a.addr = msg.sender;
        a.gigID = id;
        a.price = _price;
        AllSellers.push(msg.sender);
         _tokenIdCounter.increment();
    }
    function gigDetails(uint _id) public view returns (SellerDetails memory) {
        return Seller[_id];
    }

    function hire(uint _id) public{
        require(Seller[_id].gigID == _id, 'invalid ID');
        Seller[_id].offer = true;
        buyer[_id].hiredGigID = _id;
        buyer[_id].buyerAddress = msg.sender;   
    }
    function AcceptOrReject(uint _id, uint8 _stat)public {
         require(_stat == 1 || _stat == 0, "invalid input");
         require(Seller[_id].gigID == _id, 'invalid ID');
         require(Seller[_id].addr == msg.sender, 'not seller');
        if(_stat == 0){
            Seller[_id].offer = false; 
            delete buyer[_id]; 
        }else if (_stat == 1){
            Seller[_id].accepted = true;            
        }
    }

    function viewOffer(uint _id) public view returns (bool){
        return Seller[ _id].offer;
    }

    function payWithEth(address _recipient, uint id) public payable {
        require(Seller[id].accepted, "offer not accepted");
        require(Seller[id].gigID == id, "invalid ID");
        require(Seller[id].price == msg.value, "not enough");
        uint agentIndex = getRandomAgent();
        Escrow.depositByETH{value: msg.value}(_recipient, agents[agentIndex]);
        AgentTorelease[agents[agentIndex]].selected[id] = true;
        AgentTorelease[agents[agentIndex]].moderations.push(id);
        emit deposit(msg.sender, _recipient, agents[agentIndex], id);
    }
    function payWithToken(IERC20 _token, address _recipient, uint id) public {
        require(Seller[id].accepted, "offer not accepted");
        require(Seller[id].gigID == id, "invalid ID");
        uint agentIndex = getRandomAgent();
        uint ethusdCurrentPrice = getETHUSDPrice();
        uint _amountToken = (Seller[id].price * ethusdCurrentPrice);
         _token.transferFrom(msg.sender, address(this), _amountToken);
         _token.approve(address(Escrow), _amountToken);
        Escrow.deposit(_token, _recipient, agents[agentIndex], _amountToken);
        AgentTorelease[agents[agentIndex]].selected[id] = true;
        emit deposit(msg.sender, _recipient, agents[agentIndex], id);
    }

    function getRandomAgent() internal returns (uint) {
        uint index = uint(keccak256(abi.encodePacked(nonce, block.timestamp, block.coinbase))) % agents.length;
        nonce++;
        return index;
    }
    function getETHUSDPrice() public view returns (uint) {
        ( , int price, , , ) = ETHusdpriceFeed.latestRoundData();
        return price.toUint256();
    }

    function addAgent(address _addr) public {
        require(admin == msg.sender, 'not authorized');
         agents.push(_addr);
    }

    function approveCancel(uint _id) public {
        require(buyer[_id].hiredGigID == _id, "invalid id");
        require(buyer[_id].buyerAddress == msg.sender, 'invalid buyer');
        Escrow.approveCancel(_id);
    }
    function buyerCancel(uint _id)public {
        require(buyer[_id].hiredGigID == _id, "invalid id");
        require(buyer[_id].buyerAddress == msg.sender, 'invalid buyer');
        Escrow.cancel(_id);
        uint amount_ = Seller[_id].price;
         (bool sent, ) = payable(msg.sender).call{value: (amount_)}("");
        require(sent, "Failed to send Ether");
    }
    //release handled by escrow
    //freelancer cancel from escrow cancel
    //agent cancel from escrow cancel

    receive()external payable{}
    fallback()external payable{}
}


