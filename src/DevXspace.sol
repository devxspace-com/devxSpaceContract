// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;
import "../lib/openzeppelin-contracts/contracts/utils/Counters.sol";
import "lib/chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "lib/openzeppelin-contracts/contracts/utils/math/SafeCast.sol";
// import "src/interface.sol/Iescrow.sol";
import "./escrow.sol";

//creates gig details ----DONE
//allows hire ------ DONE
//can mark job completed --- DONE
//allows freelancer to accept ----DONE
//notifies employer when job is done --- DONE
//notifies agents when work is done ----DONE
//
contract DevXspace is EscrowByAgentV2 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;
    Counters.Counter private AgentIDCounter;
    using SafeCast for int256;
    struct Tasks {
        uint256 task_id;
        uint256 price;
        uint256 deadline;
        bool completed;
        bool aborted;
        bool finalized;
        bool accepted;
        string description;
        bool reject_submission;
        bool accept_submission;
        bool rejected;
        bool submitted;
        address buyer_address;
        string title;
        address agent_address;
        address developer_address;
        bool ongoing;  
        uint pool_id; 
    }


    struct Gigs{
        address developer;
        string about;
        string image_uri;
        uint gigID;
        uint price;
    }
    struct SellerDetails {
        address seller_address;
        string[] skills;
        string username;
        string avatar_url;
        mapping (uint => Gigs) gig;
        mapping (uint => Tasks) task;
        uint[] gigid;
        uint[] tasks_id;
    }
    uint256 TaskId;
    uint256 GigId;
    struct Buyerdetails{
        address buyer_address;
        string username;
        string avatar_url;
        mapping (uint => Tasks) task;
        uint[] tasks_id;
    }
    struct AgentDetails {
        mapping(address => bool) agentStatus;
        mapping(uint => bool) selected;
        uint[] moderations;
    }


    address admin;

    mapping (uint => Gigs) private allgigs;

    mapping(address => SellerDetails) Seller;
    mapping(address => Buyerdetails) Buyer;
    mapping(address => AgentDetails) AgentTorelease;
    AggregatorV3Interface internal ETHusdpriceFeed;
    address[] AllSellers;
    address[] agents;
    uint agentIDNumber;
    uint private nonce;

    event Deposit(address sender, address recipient, address agent, uint gigID);

constructor(address _agents, uint _nonce,  uint96 _feePercent,
        uint96 _agentFeePercent,
        uint64 _cancelLockDays )EscrowByAgentV2(_feePercent, _agentFeePercent, _cancelLockDays){
    agents.push(_agents);
    AgentTorelease[_agents].agentStatus[_agents] = true;
    // Escrow = IEscrowByAgent(_escrow);
    nonce = _nonce;
    admin = msg.sender;
    ETHusdpriceFeed = AggregatorV3Interface(0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419);
}

    function createBuyerProfile(address _address, string memory _username, string memory _avatar) public{
        require(_address !=address(0), "address zero");
        Buyerdetails storage new_buyer = Buyer[_address];
        new_buyer.buyer_address = _address;
        new_buyer.username = _username;
        new_buyer.avatar_url = _avatar;
    }

     function createSellerProfile(address _address, string[] memory _skills, string memory _username, string memory _avatar) public{
        require(_address !=address(0), "address zero");
        SellerDetails storage new_seller = Seller[_address];
        new_seller.seller_address = _address;
        new_seller.skills = _skills;
        new_seller.username = _username;
        new_seller.avatar_url = _avatar;
    }

    function createGig(uint _price, string memory _about, string memory _image_uri) public returns(uint gig_id){
       SellerDetails storage seller = Seller[msg.sender];
       uint id = GigId;
       require(seller.seller_address !=address(0), "not a seller");
       Gigs storage new_gig = seller.gig[id];
       new_gig.developer = msg.sender;
       new_gig.about = _about;
       new_gig.image_uri = _image_uri;
       new_gig.price = _price;
       seller.gigid.push(id);
       gig_id = id;
       GigId +=1;
    }

    /// returns the gigs for a particular seller
    function getGig(address _seller, uint Id) public view returns (Gigs memory) {
        SellerDetails storage seller = Seller[_seller];
        require(seller.seller_address != address(0), "not a seller");
        return seller.gig[Id];
    }

/// @dev returns all gigs created on the contract
    function getAllgigs() public view returns(Gigs[] memory){
        uint id = GigId;
      Gigs[] memory allGigs = new Gigs[](id);

    for (uint i = 1; i <= id; i++) {
        Gigs storage gig = allgigs[i];
        allGigs[i-1] = gig;
    }

    return allGigs;
}
  function getTasksForSeller(address _seller) public view returns (Tasks[] memory) {
    SellerDetails storage seller = Seller[_seller];
    require(seller.seller_address != address(0), "not a seller");

    uint numTasks = seller.tasks_id.length;
    Tasks[] memory allTasks = new Tasks[](numTasks);

    for (uint i = 0; i < numTasks; i++) {
        uint taskId = seller.tasks_id[i];
        Tasks storage task = seller.task[taskId];
        allTasks[i] = task;
    }

    return allTasks;
}

function getTasksForBuyer(address _buyer) public view returns (Tasks[] memory) {
    Buyerdetails storage buyer = Buyer[_buyer];
require(buyer.buyer_address != address(0), "not a buyer");
    uint numTasks = buyer.tasks_id.length;
    Tasks[] memory allTasks = new Tasks[](numTasks);

    for (uint i = 0; i < numTasks; i++) {
        uint taskId = buyer.tasks_id[i];
        Tasks storage task = buyer.task[taskId];
        allTasks[i] = task;
    }

    return allTasks;
}

function hire(
    string memory _description, string memory _title,
    address _developer, uint _deadline, uint _price
) public returns(uint _id) {
    Buyerdetails storage buyer = Buyer[msg.sender];
    require(buyer.buyer_address != address(0), "not a buyer");
    SellerDetails storage hired_seller = Seller[_developer];
    require(hired_seller.seller_address != address(0), "not a seller");

    TaskId += 1;
    uint id = TaskId;

    Tasks storage new_task = buyer.task[id];
    new_task.description = _description;
    new_task.title = _title;
    new_task.price = _price;
    new_task.deadline = _deadline;
    new_task.developer_address = _developer;
    new_task.buyer_address = msg.sender;

    hired_seller.task[id] = new_task;
    hired_seller.tasks_id.push(id);
    buyer.task[id] = new_task;
    buyer.tasks_id.push(id);

    _id = id;

    // uint agent_id = getRandomAgent();
    // address randomAgent = agents[agent_id];
    // new_task.agent_address = randomAgent;
    // payWithEth(_developer, randomAgent);
}


    function AcceptTask(uint task_id)public {
        SellerDetails storage seller = Seller[msg.sender];
        require(seller.seller_address !=address(0), "zero address");
        Tasks storage target_task = seller.task[task_id];
        require(target_task.developer_address !=address(0), "task does not exist");
        require(target_task.developer_address ==msg.sender, "not task owner");
        require(target_task.aborted != true);
        require(target_task.accepted !=true, "task accepted previously");
        Buyer[target_task.buyer_address].task[task_id].accepted = true;
        target_task.accepted = true;

    }

    function RejectTask(uint task_id)public {
        Tasks storage target_task = Seller[msg.sender].task[task_id];
        require(target_task.developer_address != address(0), "you don't own this task");
        require(target_task.aborted != true);
        require(target_task.accepted !=true, "task accepted previously");
        Buyer[target_task.buyer_address].task[task_id].rejected = true;
        target_task.rejected = true;

    }

     function AbortTask(uint task_id)public {
        Tasks storage target_task = Seller[msg.sender].task[task_id];
        require(target_task.developer_address == msg.sender, "you don't own this task");
        require(target_task.aborted != true, "task already aborted");
        require(target_task.ongoing==true, "task not started");
        require(target_task.accepted==true);
        Buyer[target_task.buyer_address].task[task_id].aborted = true;
        target_task.aborted = true;

    }


    function SubmitTask(uint task_id) public{
        Tasks storage target_task = Seller[msg.sender].task[task_id];
        require(target_task.ongoing, "not an ongoing task");
        require(target_task.developer_address==msg.sender, "not your task");
        require(target_task.accepted==true, "task not accepted");
        Buyer[target_task.buyer_address].task[task_id].completed = true;
        Buyer[target_task.buyer_address].task[task_id].submitted = true;
        target_task.completed = true;
        target_task.submitted = true;
    }
    function AcceptSubmission(uint task_id)public {
        Tasks storage target_task = Buyer[msg.sender].task[task_id];
        require(target_task.buyer_address == msg.sender, "you don't own this task");
        require(target_task.aborted != true, "task aborted");
        require(target_task.submitted==true, "task not submitted");
        require(target_task.completed == true, "task yet to be submitted");
        Seller[target_task.developer_address].task[task_id].finalized = true;
        Seller[target_task.developer_address].task[task_id].accept_submission = true;
        target_task.finalized = true;
        target_task.accept_submission = true;

    }

     function RejectSubmission(uint task_id)public {
        Tasks storage target_task = Buyer[msg.sender].task[task_id];
        require(target_task.buyer_address == msg.sender, "you don't own this task");
        require(target_task.aborted != true, "task aborted");
        require(target_task.submitted==true, "task not submitted");
        require(target_task.completed == true, "task yet to be submitted");
        Seller[target_task.developer_address].task[task_id].finalized = false;
        Seller[target_task.developer_address].task[task_id].reject_submission = true;
        target_task.finalized = false;
        target_task.accept_submission = true;

    }


    function payWithEth(address _recipient, uint task_id) public payable returns(uint _pool_id) {
        SellerDetails storage seller = Seller[_recipient];
        Buyerdetails storage buyer = Buyer[msg.sender];
        Tasks storage task = seller.task[task_id];
        require(task.accepted==true, "task not accepted yet");
        require(task.developer_address == _recipient, "invalid recipient");
        require(task.buyer_address != address(0), "task unavailable");
        require(task.buyer_address== msg.sender, "not task owner");
        uint price = task.price;
        require(msg.value==price, "not enough ether");
        task.ongoing=true;
        buyer.task[task_id].ongoing = true;
        // depositByETH{value: msg.value}(_recipient, _agent);
        uint agent_id = getRandomAgent();
        address _agent = agents[agent_id];
        _pool_id = _deposit(address(0x0), msg.sender, _recipient, _agent, msg.value);
        buyer.task[task_id].pool_id = _pool_id;
        AgentTorelease[agents[agent_id]].selected[_pool_id] = true;
        AgentTorelease[agents[agent_id]].moderations.push(_pool_id);
        emit Deposit(msg.sender, _recipient, agents[agent_id], _pool_id);
    }

    function payWithToken(IERC20 _token, address _recipient, uint task_id) public returns(uint pool_id)  {
    SellerDetails storage seller = Seller[_recipient];
    Tasks storage task = seller.task[task_id];
    require(task.accepted==true, "task not accepted yet");
    require(task.developer_address == _recipient, "invalid recipient");
    require(task.buyer_address != address(0), "task unavailable");
    uint agentIndex = getRandomAgent();
    uint ethusdCurrentPrice = getETHUSDPrice();
    uint _amountToken = (task.price * ethusdCurrentPrice);
    _token.transferFrom(msg.sender, address(this), _amountToken);
    _token.approve(agents[agentIndex], _amountToken);
    require(_token.balanceOf(msg.sender) >= _amountToken, "balance not enough");
    require(_token.allowance(msg.sender, address(this)) >= _amountToken, "allowance not enough");
    pool_id = _deposit(address(_token), msg.sender, _recipient, agents[agentIndex], _amountToken);
    AgentTorelease[agents[agentIndex]].selected[pool_id] = true;
    emit Deposit(msg.sender, _recipient, agents[agentIndex], pool_id);
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


    receive()external payable{}
    fallback()external payable{}
    
}
    //release handled by escrow
    //freelancer cancel from escrow cancel
    //agent cancel from escrow cancel



